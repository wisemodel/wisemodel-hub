import argparse

from wisemodel_hub import download_with_git, file_download, lfs_file_download, snapshot_download


def wm_download():
    parser = argparse.ArgumentParser(
        description="从 wisemodel hub 下载文件或目录。如果提示输入用户名和密码，请输入登录wisemodel.cn的用户名和密码。"
    )
    parser.add_argument("repo_id", type=str, help="仓库 ID。必填")
    parser.add_argument("--file_name", type=str, default=None, help="要下载的文件名（若下载目录则留空）。", nargs="?")
    parser.add_argument(
        "--repo_type", type=str, default="models", help="仓库类型（models, datasets, codes）。默认值：models"
    )
    parser.add_argument("--local_dir", type=str, default=None, help="本地下载目录。默认值：None")
    parser.add_argument("--branch", type=str, default="main", help="分支名称。默认值：main")
    parser.add_argument(
        "--num_parts", type=int, default=1, help="并行下载线程数。默认值：1。设置值超过1 则使用分块下载"
    )
    parser.add_argument("--force_download", action="store_true", help="强制下载。默认值：False")
    parser.add_argument("--pattern", type=str, default=None, help="用于过滤文件名的匹配字符串。默认值：None")
    parser.add_argument(
        "--use_git", action="store_true", help="使用 git 下载。默认值：False。如果使用git，则必须提供 access_token"
    )
    parser.add_argument("--access_token", help="请到主站->用户中心->Token与Key 页面中查找。")

    args = parser.parse_args()

    if args.use_git:
        download_with_git(
            access_token=args.access_token,
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            pattern=args.pattern,
            local_dir=args.local_dir,
            branch=args.branch,
        )
    else:
        if args.file_name:
            if args.num_parts > 1:
                lfs_file_download(
                    repo_id=args.repo_id,
                    file_name=args.file_name,
                    repo_type=args.repo_type,
                    local_dir=args.local_dir,
                    branch=args.branch,
                    num_parts=args.num_parts,
                    force_download=args.force_download,
                )
            else:
                file_download(
                    repo_id=args.repo_id,
                    file_name=args.file_name,
                    repo_type=args.repo_type,
                    local_dir=args.local_dir,
                    branch=args.branch,
                    force_download=args.force_download,
                )
        else:
            snapshot_download(
                repo_id=args.repo_id,
                repo_type=args.repo_type,
                local_dir=args.local_dir,
                branch=args.branch,
                pattern=args.pattern,
                num_parts=args.num_parts,
                force_download=args.force_download,
            )


if __name__ == "__main__":
    wm_download()
