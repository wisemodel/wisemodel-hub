import fnmatch
import hashlib
import json
import logging
import os
import subprocess

import gitlab
import requests

from .auth import get_local_token, login_required
from .constants import CACHE_PATH, HEADERS, TEN_MB, WM_ENDPOINT, WM_GITLAB_ENDPOINT, WM_URL_BASE, WM_URL_LIST_BRANCH


logger = logging.getLogger(__name__)


# Get file names from GitLab repo based on repo id
def get_file_names(repo_id, path="", revision="main"):
    gl = gitlab.Gitlab(WM_GITLAB_ENDPOINT)
    project = gl.projects.get(repo_id)
    files = []
    # 遍历文件树
    items = project.repository_tree(path=path, ref=revision, all=True)
    for item in items:
        if item["type"] == "tree":  # 如果是目录，递归获取子目录内容
            files.extend(get_file_names(repo_id, path=item["path"], revision=revision))
        elif item["type"] == "blob":  # 如果是文件，添加到文件列表
            files.append(item["path"])

    return files

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


def filter_files_with_fnmatch(file_list, pattern=None):
    """
    使用 fnmatch 模式过滤文件列表，返回匹配的文件子列表。
    如果未提供模式，返回原文件列表。

    参数：
    file_list - 文件列表
    pattern - fnmatch 模式（可选）

    返回：
    匹配的文件子列表
    """
    if not pattern:
        return file_list
    return [file for file in file_list if fnmatch.fnmatch(file, pattern)]


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


@login_required
def get_repo_branch_list(repo_id, repo_type):
    token = get_local_token()
    remote_project_url = os.path.join(WM_URL_BASE, repo_type, repo_id)

    request = {"project_path": remote_project_url}
    headers = {"authorization": f"Bearer {token}"}
    response = requests.post(WM_URL_LIST_BRANCH, data=json.dumps(request), headers=headers)
    json_response = response.json()

    if json_response["code"] == 0:
        return [item["branch"] for item in json_response["data"]["list"]]
    elif json_response["code"] == 10003:
        raise ValueError(
            f"Not found any branches in repository: {repo_type}/{repo_id}, you can check value of papameters repo_id and repo_type."
        )
    else:
        raise ValueError("Failed to get branch list from remote server.")


def is_branch_exist(repo_id, repo_type, branch_name):
    branch_list = get_repo_branch_list(repo_id, repo_type)
    logger.info(f"check if branch {branch_name} in repository {repo_type}/{repo_id}")
    return branch_name in branch_list

def get_filtered_paths(folder_path, pattern):
    paths = []
    pattern = "*" if pattern is None else pattern
    for root, _, files in os.walk(folder_path):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), folder_path)
            if fnmatch.fnmatch(relative_path, pattern):
                full_path = os.path.join(root, file)
                paths.append((relative_path, full_path))
    return paths
