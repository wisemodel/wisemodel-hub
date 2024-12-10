import os
import re
import subprocess

import gitlab

from .constants import WM_GITLAB_ENDPOINT
from .utils import ensure_git_lfs_installed, is_git_repository, is_sparse_checkout


class GitDownloader:
    def __init__(self, access_token, cache_path):
        self.access_token = access_token
        self.cache_path = cache_path
        self.gitlab_url = "https://oauth2:{}@www.wisemodel.cn/{}.git"

    def snapshot_download(self, repo_id, repo_type=None, local_dir=None, revision="master"):
        ensure_git_lfs_installed()

        # 修改连接字符串根据库类型
        if repo_type == "codes":
            repo_url = self.gitlab_url.format(self.access_token, os.path.join("codes", repo_id))
        else:
            repo_url = self.gitlab_url.format(self.access_token, repo_id)

        if repo_type is None and local_dir is None:
            local_dir = os.path.join(self.cache_path, repo_id.replace("/", "_"))
        elif local_dir is None:
            local_dir = os.path.join(self.cache_path, "_".join([repo_type, repo_id.replace("/", "_")]))

        os.makedirs(local_dir, exist_ok=True)
        if not is_git_repository(local_dir):
            subprocess.run(["git", "clone", "--depth=1", "-b", revision, repo_url, local_dir], check=True)
        else:
            if is_sparse_checkout(local_dir):
                subprocess.run(["git", "sparse-checkout", "disable"], cwd=local_dir, check=True)
            subprocess.run(["git", "-C", local_dir, "pull", "origin", revision], cwd=local_dir, check=True)

        print(f"Repository {repo_id} downloaded successfully to {local_dir}.")

    def download_file(self, repo_id, repo_type=None, pattern=None, local_dir=None, revision="main"):
        ensure_git_lfs_installed()

        # 修改连接字符串根据库类型
        if repo_type == "codes":
            repo_id = os.path.join("codes", repo_id)
            repo_url = self.gitlab_url.format(self.access_token, repo_id)
        else:
            repo_url = self.gitlab_url.format(self.access_token, repo_id)

        if local_dir is None:
            local_dir = os.path.join(self.cache_path, repo_id.replace("/", "_"))

        # 获取所有文件
        all_files = self.get_all_files(repo_id, path="", revision=revision)
        # 使用正则表达式筛选文件
        regex = re.compile(pattern)
        matching_files = [file for file in all_files if regex.match(file)]
        print(matching_files)

        os.makedirs(local_dir, exist_ok=True)

        if not is_git_repository(local_dir):
            # 初始化 Git 存储库
            subprocess.run(["git", "init", f"--initial-branch={revision}"], cwd=local_dir, check=True)
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=local_dir, check=True)

            # 配置稀疏检出
            subprocess.run(["git", "config", "core.sparseCheckout", "true"], cwd=local_dir, check=True)

            # 将匹配的文件写入 .git/info/sparse-checkout 文件中
            sparse_checkout_file = os.path.join(local_dir, ".git", "info", "sparse-checkout")
            with open(sparse_checkout_file, "w") as f:
                for file in matching_files:
                    f.write(f"{file}\n")
            # 拉取匹配的文件
            subprocess.run(["git", "pull", "origin", revision], cwd=local_dir, check=True)  # 默认使用 main 分支
        else:
            for file_path in matching_files:
                result = subprocess.run(
                    ["git", "ls-tree", "-r", f"origin/{revision}", "--", file_path],
                    cwd=local_dir,
                    capture_output=True,
                    text=True,
                )
                object_id = result.stdout.split()[2]
                # 创建文件目录
                save_file_path = os.path.join(local_dir, file_path)
                os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
                # 下载并保存文件
                with open(save_file_path, "wb") as f:
                    subprocess.run(["git", "cat-file", "-p", object_id], cwd=local_dir, stdout=f)

        print(f"Files matching pattern {pattern} downloaded successfully from {repo_id} to {local_dir}.")

    def get_all_files(self, repo_id, path="", revision="main"):
        gl = gitlab.Gitlab(WM_GITLAB_ENDPOINT, private_token=self.access_token)
        project = gl.projects.get(repo_id)
        files = []

        # 遍历文件树
        items = project.repository_tree(path=path, ref=revision, all=True)
        for item in items:
            if item["type"] == "tree":  # 如果是目录，递归获取子目录内容
                files.extend(self.get_all_files(repo_id, path=item["path"], revision=revision))
            elif item["type"] == "blob":  # 如果是文件，添加到文件列表
                files.append(item["path"])

        return files
