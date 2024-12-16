from .constants import CACHE_PATH, RETRY_TIMES
from .download_with_resume import GitFileDownload
from .git_downloader import GitDownloader
from .parallel_download_with_resume import LFSDownload
from .utils import filter_files_with_fnmatch, get_file_names, is_branch_exist, is_file_downloaded, is_greater_than_10mb


def snapshot_download(
    repo_id, repo_type="models", local_dir=None, branch="main", pattern=None, num_parts=8, force_download=False
):
    """
    snapshot_download 下载指定仓库的指定版本。
    ------------------------------------------

    下载指定仓库的指定版本。如果指定本地文件夹，则下载到本地文件夹；否则，下载到默认缓存目录。

    参数：
    ::::::::::
    - **repo_id**: 仓库ID
    - **repo_repo**: 仓库类型，可选值：'models'、'datasets'、'codes'
    - **local_dir**: 本地文件夹路径，默认为None，即下载到默认缓存目录
    - **revision**: 版本号，默认为"main"
    - **pattern**: fnmatch格式的匹配字符串，用于过滤文件名，默认为None，即不过滤
    - **num_parts**: 下载分块数，默认为8
    - **force_download**: 是否强制下载，如果本地已存在，则重新下载，默认为False
    """
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")

    file_names = get_file_names(repo_id, revision=branch)
    file_names = filter_files_with_fnmatch(file_names, pattern)
    for file_name in file_names:
        try_times = 0
        while try_times < RETRY_TIMES + 1:
            if is_file_downloaded(repo_id, file_name, branch) and not force_download:
                print(f"{file_name} already exists in cache.")
                break
            try:
                try_times += 1
                print(f"Downloading {file_name}...")
                if is_greater_than_10mb(repo_id, file_name, branch):
                    lfs_file_download(
                        repo_id,
                        file_name,
                        local_dir=local_dir,
                        branch=branch,
                        num_parts=num_parts,
                        force_download=force_download,
                    )
                else:
                    file_download(
                        repo_id, file_name, local_dir=local_dir, branch=branch, force_download=force_download
                    )
                break
            except Exception as e:
                print(f"Failed to download {file_name}: {e}")
                if try_times < RETRY_TIMES + 1:
                    print(f"Retrying {try_times}...")
                else:
                    print(f"Failed to download {file_name} after {try_times-1} retries.")


def lfs_file_download(
    repo_id, file_name, repo_type="models", local_dir=None, branch="main", num_parts=8, force_download=False
):
    """
    lfs_file_download 下载大文件
    ---------------------------------

    超过10MB被认为是大文件

    参数:
    ::::::::::
    - **repo_id**: 仓库ID
    - **file_name**: 文件名
    - **repo_repo**: 仓库类型，可选值：'models'、'datasets'、'codes'
    - **local_dir**: 本地文件夹路径，默认为None，即下载到默认缓存目录
    - **revision**: 版本号，默认为"main"
    - **num_parts:** 下载分块数，默认为8
    - **force_download**: 是否强制下载，如果本地已存在，则重新下载，默认为False
    """
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")

    downloader = LFSDownload(
        repo_id, file_name, local_dir=local_dir, revision=branch, num_parts=num_parts, force_download=force_download
    )
    downloader.download()


def file_download(repo_id, file_name, repo_type="models", local_dir=None, branch="main", force_download=False):
    """
    file_download 下载单个文件
    ----------------------------

    下载文件，小于10MB被认为是小文件

    参数：
    ::::::::::
    - **repo_id** - 仓库ID
    - **file_name** - 文件名
    - **repo_repo**: 仓库类型，可选值：'models'、'datasets'、'codes'
    - **local_dir** - 本地文件夹路径，默认为None，即下载到默认缓存目录
    - **revision** - 版本号，默认为"main"
    - **force_download** - 是否强制下载，如果本地已存在，则重新下载，默认为False
    """
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")
    downloader = GitFileDownload(repo_id)
    downloader.download_file(file_name, revision=branch, local_dir=local_dir, force_download=force_download)


def download_with_git(access_token, repo_id, repo_type="models", pattern=None, local_dir=None, branch="main"):
    """
    download_with_git 利用本地的git工具下载文件到本地仓库
    -------------------------------------------------------

    本地必须安装git工具，并检查git-lfs是否安装。
    `git lfs install`

    参数：
    ::::::::::
    - **access_token** - # 在主站登录后，在https://www.wisemodel.cn/my-token 页面中，`git token`tab页内获取
    - **repo_id** - 仓库id，格式为 'owner/repo_name'
    - **repo_type** - 仓库类型，可选值：'models'、'datasets'、'codes'
    - **pattern** - fnmatch格式的匹配字符串，用于过滤文件名，默认为None，即不过滤
    - **local_dir** - 本地文件夹路径
    - **branch** - wisemodel使用git管理仓库，此参数是git分支名

    抛出异常：
    ::::::::::
    - **EnvironmentError** - git lfs 未安装时抛出
    """
    if not is_branch_exist(repo_id, repo_type, branch):
        raise ValueError(f"仓库 {repo_id} 不存在分支 {branch}")

    downloader = GitDownloader(access_token, cache_path=CACHE_PATH)

    if pattern is None:
        downloader.snapshot_download(repo_id, repo_type, local_dir, branch)
    else:
        downloader.download_file(repo_id, repo_type, pattern, local_dir, branch)
