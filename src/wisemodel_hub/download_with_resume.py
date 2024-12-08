import os
import shutil
from copy import deepcopy

import requests
from tqdm import tqdm

from .constants import CACHE_PATH, HEADERS, WM_ENDPOINT
from .utils import get_remote_file_size_with_url


class GitFileDownload:
    def __init__(self, repo_id):
        self.repo_id = repo_id
        self.cache_dir = os.path.join(CACHE_PATH, repo_id.replace("/", "_"))

    def download_file(self, file_name, revision="main", local_dir=None, force_download=False):
        repo_id = self.repo_id
        file_url = WM_ENDPOINT + f"/file-proxy/{repo_id}/-/raw/{revision}/{file_name}"

        # Get cache path and incomplete path
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_path = os.path.join(self.cache_dir, file_name)
        if os.path.exists(cache_path) and not force_download:
            print(f"{file_name} already exists in cache.")
            return cache_path
        incomplete_path = cache_path + ".incomplete"

        # Check for incomplete download and get resume size
        resume_size = 0
        if os.path.exists(incomplete_path):
            resume_size = os.path.getsize(incomplete_path)

        # Download with resume support
        print(f"Downloading from {file_url}")
        print(f"Cache path: {cache_path}")
        self._download_with_resume(file_url, cache_path, incomplete_path, resume_size)

        # Copy to local directory or return cached path
        if local_dir:
            local_path = os.path.join(local_dir, file_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copyfile(cache_path, local_path)
            return local_path
        else:
            return cache_path

    def _download_with_resume(self, url, cache_path, incomplete_path, resume_size):
        # headers = {"Range": f"bytes={resume_size}-"} if resume_size else None
        headers = deepcopy(HEADERS)
        if resume_size:
            headers["Range"] = f"bytes={resume_size}-"

        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()

            total_size = get_remote_file_size_with_url(url)
            print(f"file total_size:{total_size}")

            progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True, initial=resume_size)

            # Create incomplete file if it doesn't exist

            with open(incomplete_path, "ab") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

        os.replace(incomplete_path, cache_path)


if __name__ == "__main__":
    # Example usage
    downloader = GitFileDownload("rwkv4fun/Rwkv-6-world")
    file_path = downloader.download_file("*", revision="main")
    print(file_path)
