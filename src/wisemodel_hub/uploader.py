import os

import requests
from tqdm import tqdm

from .auth import get_local_token, login, login_required, notebook_login
from .constants import WM_URL_ADDFILES, WM_URL_BASE, WM_URL_CHECK, WM_URL_MERGE, WM_URL_UPLOAD
from .git_uploader import GitUploader
from .utils import calculate_md5, filter_files_with_regex, is_notebook


@login_required
def upload_file(
    file_path,
    repo_id,
    repo_type,
    branch,
    commit_message="添加文件",
    chunk_size=5 * 1024 * 1024,
    retries=3,
    timeout=None,
):
    """
    upload_file 上传单个文件
    --------------------------------------

    上传单个文件到主站仓库。

    参数：
    :::::::::::::
    - **file_path** - 要上传文件的全路径
    - **repo_id** - 仓库id，格式为 'owner/repo_name'
    - **repo_type** - 仓库类型，可选值：'models'、'datasets'、'codes'
    - **branch** - wisemodel使用git管理仓库，此参数是git分支名
    - **commit_message** - 仓库提交信息
    - **chunk_size** - 上传时使用的分段大小，默认为5MB
    - **retries** - 上传失败重试次数
    - **timeout** - 调用主站api的超时时间，默认为None
    """
    token = get_local_token()
    file_name = os.path.basename(file_path)
    file_md5 = calculate_md5(file_path)
    remote_project_url = os.path.join(WM_URL_BASE, repo_type, repo_id)

    # Step 1: Check the file chunk status
    check_data = {"fileName": file_name, "fileMd5": file_md5, "dir": "", "project_path": remote_project_url}

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(WM_URL_CHECK, data=check_data, headers=headers)
    check_response = response.json()

    # 如果提示token失败，则重新登录
    if check_response["code"] == "B2002":
        if is_notebook():
            notebook_login(new_session=True)
        else:
            login(new_session=True)

    if check_response["code"] != 0:
        print(f"文件检查失败: {check_response['message']}")
        return

    existing_chunks = check_response["data"]["chunks"]
    if "resultCode" in check_response["data"] and check_response["data"]["resultCode"] == -1:
        existing_chunks = []

    # Step 2: Upload file chunks
    file_size = os.path.getsize(file_path)
    num_chunks = (file_size + chunk_size - 1) // chunk_size  # 计算块的数量

    with open(file_path, "rb") as f, tqdm(total=file_size, unit="B", unit_scale=True, desc=file_name) as pbar:
        for i in range(num_chunks):
            if str(i) in existing_chunks:
                f.seek(chunk_size, os.SEEK_CUR)
                pbar.update(chunk_size)  # 跳过已存在的块，并更新进度条
                continue

            chunk_data = f.read(chunk_size)
            upload_data = {"md5": file_md5, "dir": "", "chunk": i}
            files = {"file": (file_name, chunk_data)}

            for _ in range(retries):
                try:
                    response = requests.post(
                        WM_URL_UPLOAD, data=upload_data, files=files, timeout=timeout, headers=headers
                    )
                    upload_response = response.json()
                    if upload_response["code"] == 0:
                        pbar.update(len(chunk_data))
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Retry {i} due to {str(e)}")

    # Step 3: Check again the file chunk status after uploading all chunks
    response = requests.post(WM_URL_CHECK, data=check_data, headers=headers)
    check_response = response.json()

    if (
        check_response["code"] != 0
        or "resultCode" in check_response["data"]
        and check_response["data"]["resultCode"] != num_chunks
    ):
        print(f"文件检查失败或文件块数量不匹配: {check_response['message']}")
        return
    print("所有文件块已成功上传并验证")

    # Step 4: Merge file chunks
    merge_data = {"fileName": file_name, "fileMd5": file_md5, "dir": "", "project_path": remote_project_url}
    response = requests.post(WM_URL_MERGE, data=merge_data, headers=headers)
    merge_response = response.json()

    if merge_response["code"] != 0:
        print(f"文件合并失败: {merge_response['message']}")
        return

    merged_file_path = merge_response["data"]["filepath"]
    print(f"文件合并成功: {merged_file_path}")

    # Step 5: Add merged file to repository
    addfiles_data = {
        "project_path": remote_project_url,
        "branch": branch,
        "files": [merged_file_path],
        "commit": commit_message,
        "wangpan_url": "",
    }
    response = requests.post(WM_URL_ADDFILES, json=addfiles_data, headers=headers)
    addfiles_response = response.json()

    if addfiles_response["code"] != 0:
        print(f"添加文件到仓库失败: {addfiles_response['message']}")
        return

    print(f"{file_name},文件上传并添加到仓库成功")


@login_required
def push_to_hub(
    dir_path,
    repo_id,
    repo_type,
    regex_pattern=None,
    branch="master",
    commit_message="commit",
    chunk_size=5 * 1024 * 1024,
    retries=3,
    timeout=None,
):
    """
    push_to_hub 上传文件夹到主站仓库
    -----------------------------------------------

    将文件夹上传至主站仓库。

    参数：
    ::::::::::
    - **dir_path** - 要上传文件的全路径
    - **repo_id** - 仓库id，格式为 'owner/repo_name'
    - **repo_type** - 仓库类型，可选值：'models'、'datasets'、'codes'
    - **regex_pattern** - 正则表达式串，用于过滤文件
    - **branch** - wisemodel使用git管理仓库，此参数是git分支名
    - **commit_message** - 仓库提交信息
    - **chunk_size** - 上传时使用的分段大小，默认为5MB
    - **retries** - 上传失败重试次数
    - **timeout** - 调用主站api的超时时间，默认为None

    抛出异常：
    ::::::::::
    ValueError - dir_path 路径不是文件夹
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"指定路径 '{dir_path}' 不是文件夹")
    # 获取文件列表并进行正则表达式过滤
    file_list = os.listdir(dir_path)
    if regex_pattern:
        file_list = filter_files_with_regex(file_list, regex_pattern)
    for file_name in file_list:
        file_path = os.path.join(dir_path, file_name)
        upload_file(file_path, repo_id, repo_type, branch, commit_message, chunk_size, retries, timeout)


def upload_with_git(
    access_token, repo_id, repo_type, local_dir, branch="main", pattern=None, commit_message="Upload files"
):
    """
    upload_with_git 利用本地的git工具上传文件到主站仓库
    ----------------------------------------------------

    本地必须安装git工具，并检查git-lfs是否安装。
    `git lfs install`

    参数：
    ::::::::::
    - **access_token** - # 在主站登录后，在https://www.wisemodel.cn/my-token 页面中，`git token`tab页内获取
    - **repo_id** - 仓库id，格式为 'owner/repo_name'
    - **repo_type** - 仓库类型，可选值：'models'、'datasets'、'codes'
    - **local_dir** - 本地文件夹路径
    - **branch** - wisemodel使用git管理仓库，此参数是git分支名
    - **pattern** - 正则表达式串，用于匹配要操作的文件
    - **commit_message** - 仓库提交信息

    抛出异常：
    ::::::::::
    - **GitUploadError** - 在git commit 和 git push 失败时抛出
    - **ValueError** - local_dir 没有赋值时抛出
    - **EnvironmentError** - git仓库初始化失败时抛出, git lfs未安装时抛出
    """
    # 使用示例
    uploader = GitUploader(access_token=access_token, local_dir=local_dir)
    if not pattern:
        # 上传整个库
        uploader.upload_repository(
            repo_id=repo_id, repo_type=repo_type, local_dir=local_dir, revision=branch, commit_message=commit_message
        )
    else:
        # 上传匹配的文件
        uploader.upload_file(
            repo_id=repo_id,
            repo_type=repo_type,
            revision=branch,
            local_dir=local_dir,
            pattern=pattern,
            commit_message=commit_message,
        )
