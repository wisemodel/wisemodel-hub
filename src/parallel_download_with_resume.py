import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from tqdm import tqdm
from contants import WM_ENDPOINT, CACHE_PATH

class LFSDownload:
    def __init__(self, repo_id, file_name, revision='main',num_parts=8):
        self.repo_id = repo_id
        self.url = WM_ENDPOINT + f"/file-proxy/{repo_id}/-/raw/{revision}/{file_name}"
        self.cache_dir = os.path.join(CACHE_PATH, repo_id.replace("/", "_"))
        self.file_name = os.path.join(self.cache_dir, file_name)
        self.num_parts = num_parts
        self.total_size = None
        self.parts = []
        self.progress_bar = None

    def prepare(self):
        # Get the total size of the file
        res = requests.get(self.url,stream=True)
        if res.status_code == 200:
            self.total_size = int(res.headers.get("Content-Length", 0))
        res.close()

        """         
        # Get the total size of the file
        res = requests.head(self.url)
        if res.status_code == 200:
            self.total_size = int(res.headers.get("Content-Length", 0))
        """
        # Calculate the size of each part
        part_size = self.total_size // self.num_parts
        remaining = self.total_size % self.num_parts

        # Create the parts
        start = 0
        for i in range(self.num_parts):
            size = part_size
            if i == self.num_parts - 1:
                size += remaining
            self.parts.append((start, start + size, f"{self.file_name}.part{i+1}"))  # Add temporary file name
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

        headers = {"Range": f"bytes={start+resume_size}-{end-1}"}
        
        response = requests.get(self.url, headers=headers, stream=True)

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

            with open(self.file_name, "ab") as outfile:
                for start, end, temp_file in self.parts:
                    print(f"Merging part {temp_file}")
                    with open(temp_file, "rb") as infile:
                        outfile.write(infile.read())
                    os.remove(temp_file)  # Delete temporary file
        except Exception as e:
            print(f"Error merging parts: {e}")
            os.remove(self.file_name)  # Delete incomplete file
            raise e
    def run(self):
        with ThreadPoolExecutor(max_workers=self.num_parts) as executor:
            futures = [executor.submit(self.download_part, start, end, temp_file) for start, end, temp_file in self.parts]

            for future in as_completed(futures):
                future.result()

        self.merge_parts()  # Merge temporary files into final file

    def download(self):
        if os.path.exists(self.file_name):
            print(f'File "{self.file_name}" already exists. Skip downloading.')
            return 
        
        self.prepare()
        '''
        # Create an empty file or resume from existing
        if not os.path.exists(self.file_name):
            with open(self.file_name, "wb") as f:
                f.truncate(self.total_size)
        '''

        # Initialize progress bar
        self.progress_bar = tqdm(total=self.total_size, unit='B', unit_scale=True, desc=self.file_name)

        self.run()

        self.progress_bar.close()
if __name__ == "__main__":
    # Example usage
    repo_id = "OpenBMB/miniCPM-dpo-fp32"
    file_name = 'pytorch_model.bin'

    download = LFSDownload(repo_id=repo_id, file_name=file_name)
    download.download()