import os
import subprocess

from .utils import ensure_git_lfs_installed, filter_files_with_fnmatch, is_git_repository


class GitUploader:
    def __init__(self, access_token, local_dir):
        self.access_token = access_token
        self.gitlab_url = "https://oauth2:{}@www.wisemodel.cn/{}.git"
        self.local_dir = local_dir
        # 设置 core.quotepath 为 false
        subprocess.run(["git", "config", "core.quotepath", "false"], cwd=self.local_dir, check=True)

    def add_remote(self, local_dir, repo_url):
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=local_dir, check=True)

    def set_remote_url(self, local_dir, repo_url):
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=local_dir, check=True)

    def initialize_repo(self, local_dir, repo_url, branch="main"):
        if not is_git_repository(local_dir):
            subprocess.run(["git", "init", "--initial-branch", branch], cwd=local_dir, check=True)
            self.add_remote(local_dir, repo_url)

    def upload_files(self, local_dir, files, message="Upload files"):
        for file in files:
            print(f"Uploading {file}...")
            file_path = os.path.join(local_dir, file)
            if os.path.exists(file_path):
                try:
                    subprocess.run(["git", "add", file], cwd=local_dir, check=True)
                except subprocess.CalledProcessError:
                    # 如果失败，使用 --sparse 选项
                    subprocess.run(["git", "add", "--sparse", file], cwd=local_dir, check=True)
            else:
                try:
                    # 如果文件不存在，执行 git rm
                    subprocess.run(["git", "rm", file], cwd=local_dir, check=True)
                except subprocess.CalledProcessError:
                    subprocess.run(["git", "rm", "--sparse", file], cwd=local_dir, check=True)
        try:
            if len(files) > 0:
                subprocess.run(["git", "commit", "-m", message], cwd=local_dir, check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=local_dir, check=True)
        except subprocess.CalledProcessError as e:
            raise self.GitUploadError(f"Failed to upload files: {e.stderr}")

    def get_all_files(self, local_dir):
        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=local_dir, check=True, capture_output=True, text=True
        )
        all_files = []
        for line in result.stdout.splitlines():
            # 当文件名称是unicode编码时，文件名会被双引号包裹
            file_path = line[3:].strip('"')  # 'git status --porcelain' output format: XY file
            all_files.append(file_path)
        return all_files

    def upload_repository(
        self, repo_id, repo_type=None, local_dir=None, revision="main", commit_message="Upload repository"
    ):
        ensure_git_lfs_installed()
        if repo_type == "codes":
            repo_url = self.gitlab_url.format(self.access_token, os.path.join("codes", repo_id))
        else:
            repo_url = self.gitlab_url.format(self.access_token, repo_id)

        if local_dir is None:
            raise ValueError("The local directory is not specified.")

        self.initialize_repo(local_dir, repo_url, revision)

        if not is_git_repository(local_dir):
            raise EnvironmentError(f"The directory {local_dir} is not a valid git repository.")

        self.set_remote_url(local_dir, repo_url)

        all_files = self.get_all_files(local_dir)
        self.upload_files(local_dir, all_files, message=commit_message)

    def upload_file(
        self, repo_id, repo_type=None, revision="main", local_dir=None, pattern=None, commit_message="Upload file"
    ):
        ensure_git_lfs_installed()
        if repo_type == "codes":
            repo_url = self.gitlab_url.format(self.access_token, os.path.join("codes", repo_id))
        else:
            repo_url = self.gitlab_url.format(self.access_token, repo_id)

        if local_dir is None:
            raise ValueError("The local directory is not specified.")

        self.initialize_repo(local_dir, repo_url, revision)

        if not is_git_repository(local_dir):
            raise EnvironmentError(f"The directory {local_dir} is not a valid git repository.")

        self.set_remote_url(local_dir, repo_url)

        matching_files = filter_files_with_fnmatch(self.get_all_files(local_dir, pattern))
        print(f"matching_files: {matching_files}")
        self.upload_files(local_dir, matching_files, message=commit_message)
