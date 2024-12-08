from .constants import RETRY_TIMES
from .download_with_resume import GitFileDownload
from .parallel_download_with_resume import LFSDownload
from .utils import filter_files_with_regex, get_file_names, is_file_downloaded, is_greater_than_10mb


def snapshot_download(repo_id, local_dir=None, revision="main", regex_pattern=None, num_parts=4, force_download=False):
    """
    snapshot_download 下载指定仓库的指定版本。
    ------------------------------------------

    下载指定仓库的指定版本。如果指定本地文件夹，则下载到本地文件夹；否则，下载到默认缓存目录。

    参数：
    ::::::::::
    - **repo_id**: 仓库ID
    - **local_dir**: 本地文件夹路径，默认为None，即下载到默认缓存目录
    - **revision**: 版本号，默认为"main"
    - **regex_pattern**: 正则表达式，用于过滤文件名，默认为None，即不过滤
    - **num_parts**: 下载分块数，默认为4
    - **force_download**: 是否强制下载，如果本地已存在，则重新下载，默认为False
    """
    file_names = get_file_names(repo_id, revision)
    file_names = filter_files_with_regex(file_names, regex_pattern)
    for file_name in file_names:
        try_times = 0
        while try_times < RETRY_TIMES + 1:
            if is_file_downloaded(repo_id, file_name, revision) and not force_download:
                print(f"{file_name} already exists in cache.")
                break
            try:
                try_times += 1
                print(f"Downloading {file_name}...")
                if is_greater_than_10mb(repo_id, file_name, revision):
                    lfs_file_download(
                        repo_id,
                        file_name,
                        local_dir=local_dir,
                        revision=revision,
                        num_parts=num_parts,
                        force_download=force_download,
                    )
                else:
                    file_download(
                        repo_id, file_name, local_dir=local_dir, revision=revision, force_download=force_download
                    )
                break
            except Exception as e:
                print(f"Failed to download {file_name}: {e}")
                if try_times < RETRY_TIMES + 1:
                    print(f"Retrying {try_times}...")
                else:
                    print(f"Failed to download {file_name} after {try_times-1} retries.")


def lfs_file_download(repo_id, file_name, local_dir=None, revision="main", num_parts=8, force_download=False):
    """
    lfs_file_download 下载大文件
    ---------------------------------

    超过10MB被认为是大文件

    参数:
    ::::::::::
    - **repo_id**: 仓库ID
    - **file_name**: 文件名
    - **local_dir**: 本地文件夹路径，默认为None，即下载到默认缓存目录
    - **revision**: 版本号，默认为"main"
    - **num_parts:** 下载分块数，默认为8
    - **force_download**: 是否强制下载，如果本地已存在，则重新下载，默认为False
    """
    downloader = LFSDownload(
        repo_id, file_name, local_dir=local_dir, revision=revision, num_parts=num_parts, force_download=force_download
    )
    downloader.download()


def file_download(repo_id, file_name, local_dir=None, revision="main", force_download=False):
    """
    file_download 下载单个文件
    ----------------------------

    下载文件，小于10MB被认为是小文件

    参数：
    ::::::::::
    - **repo_id** - 仓库ID
    - **file_name** - 文件名
    - **local_dir** - 本地文件夹路径，默认为None，即下载到默认缓存目录
    - **revision** - 版本号，默认为"main"
    - **force_download** - 是否强制下载，如果本地已存在，则重新下载，默认为False
    """
    downloader = GitFileDownload(repo_id)
    downloader.download_file(file_name, revision=revision, local_dir=local_dir, force_download=force_download)