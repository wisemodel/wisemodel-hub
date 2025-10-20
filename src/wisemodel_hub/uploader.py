import concurrent.futures
import os

import requests
from tqdm import tqdm

from .auth import get_local_token, login, login_required, notebook_login
from .constants import WM_URL_ADDFILES, WM_URL_BASE, WM_URL_CHECK, WM_URL_MERGE, WM_URL_UPLOAD
from .git_uploader import GitUploader
from .utils import (
    calculate_md5,
    get_filtered_curr_paths,
    get_filtered_paths,
    get_repo_file_list,
    is_branch_exist,
    is_notebook,
)


@login_required
def upload_file(
    file_path,
    repo_id,
    repo_type="models",
    branch="main",
    commit_message="添加文件",
    chunk_size=5 * 1024 * 1024,
    retries=3,
    timeout=None,
    repo_dir=None
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
    - **repo_dir** - 远程仓库的相对路径，默认为None，即上传到仓库根目录
    """
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")
    token = get_local_token()
    file_name = os.path.basename(file_path)
    file_md5 = calculate_md5(file_path)
    remote_project_url = f"{WM_URL_BASE}/{repo_type}/{repo_id}"

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
        token = get_local_token()
        headers = {"Authorization": f"Bearer {token}"}

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
    if not repo_dir:
        repo_dir = ""
    addfiles_data = {
        "project_path": remote_project_url,
        "branch": branch,
        "files": [merged_file_path],
        "commit": commit_message,
        "wangpan_url": "",
        "git_folder": repo_dir,
    }
    print(f"addfiles_data: {addfiles_data}")
    print(f"headers: {headers}")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(WM_URL_ADDFILES, json=addfiles_data, headers=headers)
    addfiles_response = response.json()
    print(f"addfiles_response: {addfiles_response}")

    if addfiles_response["code"] != 0:
        print(f"添加文件到仓库失败: {addfiles_response['message']}")
        return

    print(f"{file_name},文件上传并添加到仓库成功")


@login_required
def push_to_hub(
    dir_path,
    repo_id,
    repo_type="models",
    pattern=None,
    branch="main",
    commit_message="上传文件夹",
    chunk_size=5 * 1024 * 1024,
    retries=3,
    timeout=None,
    resumable: bool = True,
    workers: int = 5,
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
    - **pattern** - fnmatch格式的匹配字符串，用于过滤文件名，默认为None，即不过滤
    - **branch** - wisemodel使用git管理仓库，此参数是git分支名
    - **commit_message** - 仓库提交信息
    - **chunk_size** - 上传时使用的分段大小，默认为5MB
    - **retries** - 上传失败重试次数
    - **timeout** - 调用主站api的超时时间，默认为None
    - **resumable** - 是否开启文件夹级别的断点续传。默认为True。
    抛出异常：
    ::::::::::
    ValueError - dir_path 路径不是文件夹
    """
    if resumable:
        print("📂 断点续传模式已开启：将检查服务端已存在的文件，跳过重复上传。")
    else:
        print("📤 强制完整上传模式：将上传所有文件，忽略服务端状态。")
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")
    if not os.path.isdir(dir_path):
        raise ValueError(f"指定路径 '{dir_path}' 不是文件夹")
    all_local_files = get_filtered_paths(dir_path, pattern)

    files_to_upload = []
    skipped_count = 0

     # --- Step 0: 文件夹级别检查 ---
    if resumable:
        print("🔍 正在检查服务端已存在的文件...")

        try:

            for root, _, _ in os.walk(dir_path):
                  print(f"检查目录: {root}")
                  if root.find(".git")>=0 :
                        print ("跳过.git目录")
                        continue
#                  if root.find(".cache")>=0 :
#                        print ("跳过.cache目录")
#                        continue
                  all_local_files = get_filtered_curr_paths(root, pattern)

                  relative_path = os.path.relpath(root, dir_path)
                  gitPath=relative_path

                  if relative_path==".":
                        gitPath=""

                  repo_list=get_repo_file_list(repo_id, repo_type,gitPath,branch)

                  if repo_list:

                        print(f"📋 发现服务端已存在 {len(repo_list)} 个文件。")

                        # --- Step 1: 本地与服务端文件对比 ---
                        for rel_path, full_path in all_local_files:
                            if rel_path in repo_list:
                                print(f"🗂️ 跳过已存在的文件: {rel_path}")
                                skipped_count += 1
                            else:
                                files_to_upload.append((rel_path, full_path))
                  else:
                        print("无法获取服务端文件列表，将上传所有文件")
                        files_to_upload_data =  all_local_files # 回退到上传所有文件
                        if len(files_to_upload_data)>0:
                           files_to_upload.append(files_to_upload_data)
                        print(f"files_to_upload: {len(files_to_upload)}")

        except requests.exceptions.RequestException as e:
                    print(f"⚠️ 检查服务端文件列表时网络出错，将上传所有文件。原因: {e}")
                    files_to_upload =  all_local_files # 回退到上传所有文件

    else:
                print("📤 强制完整上传模式：将上传所有文件，忽略服务端状态。")
                files_to_upload = all_local_files

    # --- 总结与准备 ---
    total_files = len(all_local_files)
    if skipped_count > 0:
        print(f"\n--- 文件检查完毕: 共 {total_files} 个文件，已跳过 {skipped_count} 个，准备上传剩余的 {len(files_to_upload)} 个文件 ---")
    elif files_to_upload:
        print(f"\n--- 准备上传全部 {len(files_to_upload)} 个文件 ---")
    else:
        print("\n🎉 所有文件都已存在于服务端，无需上传。")
        return
    #print(files_to_upload)
    def upload_wrapper(args):
        rel_path, full_path = args[0], args[1]
        return upload_file(full_path, repo_id, repo_type, branch, commit_message, chunk_size, retries, timeout, repo_dir=os.path.dirname(rel_path))
    for rel_path, full_path in files_to_upload:
        # upload_file(full_path, repo_id, repo_type, branch, commit_message, chunk_size, retries, timeout, repo_dir=os.path.dirname(rel_path))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            list(executor.map(upload_wrapper, files_to_upload))


def upload_with_git(
    access_token,
    repo_id,
    repo_type="models",
    local_dir=None,
    branch="main",
    pattern=None,
    commit_message="Upload files",
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
    - **pattern** - fnmatch格式的匹配字符串，用于过滤文件名，默认为None，即不过滤
    - **commit_message** - 仓库提交信息

    抛出异常：
    ::::::::::
    - **GitUploadError** - 在git commit 和 git push 失败时抛出
    - **ValueError** - local_dir 没有赋值时抛出
    - **EnvironmentError** - git仓库初始化失败时抛出, git lfs未安装时抛出
    """
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")
    uploader = GitUploader(access_token=access_token, local_dir=local_dir)
    if not pattern:
        uploader.upload_repository(
            repo_id=repo_id, repo_type=repo_type, local_dir=local_dir, revision=branch, commit_message=commit_message
        )
    else:
        uploader.upload_file(
            repo_id=repo_id,
            repo_type=repo_type,
            revision=branch,
            local_dir=local_dir,
            pattern=pattern,
            commit_message=commit_message,
        )
