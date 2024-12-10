import hashlib
import os
import re
import subprocess

import gitlab
import requests

from .constants import CACHE_PATH, HEADERS, TEN_MB, WM_ENDPOINT, WM_GITLAB_ENDPOINT


# Get file names from GitLab repo based on repo id
def get_file_names(repo_id, revision="main"):
    gl = gitlab.Gitlab(WM_GITLAB_ENDPOINT)
    project = gl.projects.get(repo_id)
    files = project.repository_tree(ref=revision)
    return [file["name"] for file in files if file["type"] == "blob"]


def get_remote_file_size(repo_id, file_name, revision="main"):
    return get_remote_file_size_with_url(WM_ENDPOINT + f"/file-proxy/{repo_id}/-/raw/{revision}/{file_name}")


def get_remote_file_size_with_url(url):
    res = requests.get(url, stream=True, headers=HEADERS)
    res.raise_for_status()
    total_size = int(res.headers.get("Content-Length", 0))
    res.close()
    return total_size


def is_file_downloaded(repo_id, file_name, revision):
    cache_path = os.path.join(CACHE_PATH, repo_id.replace("/", "_"), file_name)
    if not os.path.exists(cache_path):
        return False
    local_size = os.path.getsize(cache_path)

    remote_size = get_remote_file_size(repo_id, file_name, revision)

    return remote_size == local_size


def is_greater_than_10mb(repo_id, file_name, revision="main"):
    return get_remote_file_size(repo_id, file_name, revision) > TEN_MB


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_notebook():
    try:
        from IPython import get_ipython  # type: ignore

        ip = get_ipython()
        if ip is not None and "IPKernelApp" in ip.config:
            return True
    except ImportError:
        return False
    return False


def filter_files_with_regex(file_list, regex_pattern=None):
    """
    使用正则表达式过滤文件列表，返回匹配的文件子列表。
    如果未提供正则表达式模式，返回原文件列表。

    参数：
    file_list - 文件列表
    regex_pattern - 正则表达式模式（可选）

    返回：
    匹配的文件子列表
    """
    if not regex_pattern:
        return file_list
    pattern = re.compile(regex_pattern)
    return [file for file in file_list if pattern.search(file)]


def is_git_repository(path):
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def is_sparse_checkout(path):
    sparse_checkout_file = os.path.join(path, ".git", "info", "sparse-checkout")
    if os.path.exists(sparse_checkout_file):
        with open(sparse_checkout_file, "r") as f:
            content = f.read().strip()
            if content:
                return True
    return False


def ensure_git_lfs_installed():
    try:
        subprocess.run(["git", "lfs", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise EnvironmentError("git lfs is not installed. Please install it first.")
