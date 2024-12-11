import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy

import requests
from tqdm import tqdm

from .constants import CACHE_PATH, HEADERS, WM_ENDPOINT
from .utils import get_remote_file_size_with_url


class LFSDownload:
    def __init__(self, repo_id, file_name, local_dir=None, revision="main", num_parts=8, force_download=False):
        self.repo_id = repo_id
        self.url = WM_ENDPOINT + f"/file-proxy/{repo_id}/-/raw/{revision}/{file_name}"
        self.cache_dir = os.path.join(CACHE_PATH, repo_id.replace("/", "_"))
        self.cache_file_name = os.path.join(self.cache_dir, file_name)
        self.num_parts = num_parts
        self.total_size = None
        self.parts = []
        self.progress_bar = None
        self.headers = deepcopy(HEADERS)
        self.local_dir = local_dir
        if self.local_dir:
            self.file_name = os.path.join(self.local_dir, file_name)
        self.force_download = force_download

    def prepare(self):
        self.total_size = get_remote_file_size_with_url(self.url)

        # Calculate the size of each part
        part_size = self.total_size // self.num_parts
        remaining = self.total_size % self.num_parts

        # Create the parts
        start = 0
        for i in range(self.num_parts):
            size = part_size
            if i == self.num_parts - 1:
                size += remaining
            self.parts.append((start, start + size, f"{self.cache_file_name}.part{i+1}"))  # Add temporary file name
            start += size
        os.makedirs(self.cache_dir, exist_ok=True)

    def download_part(self, start, end, temp_file):
        print(f"Downloading part {temp_file}, range: {start}-{end}")
        resume_size = 0
        # Check if the temporary part file already exists and is complete
        if os.path.exists(temp_file) and os.path.getsize(temp_file) == end - start:
            self.progress_bar.update(end - start)  # Update progress for already downloaded part
            return  # Skip downloading
        else:
            resume_size = os.path.getsize(temp_file) if os.path.exists(temp_file) else 0
            self.progress_bar.update(resume_size)  # Update progress for already downloaded part
            print(f"Resuming download of part {temp_file}, starting from {start + resume_size}")

        self.headers["Range"] = f"bytes={start+resume_size}-{end-1}"

        response = requests.get(self.url, headers=self.headers, stream=True)

        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        with open(temp_file, "ab") as f:  # Write to temporary file
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    self.progress_bar.update(len(chunk))  # Update progress bar

    def merge_parts(self):
        try:
            for start, end, temp_file in self.parts:
                if os.path.exists(temp_file):
                    if os.path.getsize(temp_file) == end - start:
                        continue
                    else:
                        raise Exception("Not all parts have been downloaded. ")

            with open(self.cache_file_name, "ab") as outfile:
                for start, end, temp_file in self.parts:
                    print(f"Merging part {temp_file}")
                    with open(temp_file, "rb") as infile:
                        outfile.write(infile.read())
                    os.remove(temp_file)  # Delete temporary file
        except Exception as e:
            print(f"Error merging parts: {e}")
            os.remove(self.cache_file_name)  # Delete incomplete file
            raise e

    def run(self):
        with ThreadPoolExecutor(max_workers=self.num_parts) as executor:
            futures = [
                executor.submit(self.download_part, start, end, temp_file) for start, end, temp_file in self.parts
            ]

            for future in as_completed(futures):
                future.result()

        self.merge_parts()  # Merge temporary files into final file

    def download(self):
        if os.path.exists(self.cache_file_name) and not self.force_download:
            print(f'File "{self.cache_file_name}" already exists. Skip downloading.')
            return

        self.prepare()

        # Initialize progress bar
        self.progress_bar = tqdm(total=self.total_size, unit="B", unit_scale=True, desc=self.cache_file_name)

        self.run()

        self.progress_bar.close()

        if self.local_dir:
            os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
            shutil.copyfile(self.cache_file_name, self.file_name)
            return self.file_name
        else:
            return self.cache_file_name
