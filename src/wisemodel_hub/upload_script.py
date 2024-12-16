import argparse
import os

from wisemodel_hub import push_to_hub, upload_file, upload_with_git


def wm_upload():
    parser = argparse.ArgumentParser(
        description="上传文件或目录到 wisemodel hub。如果提示输入用户名和密码，请输入登录wisemodel.cn的用户名和密码。"
    )
    parser.add_argument("file_path", type=str, help="要上传的文件或目录路径。必填")
    parser.add_argument("repo_id", type=str, help="仓库 ID。必填")
    parser.add_argument(
        "--repo_type", type=str, default="models", help="仓库类型（models, datasets, codes）。默认值：models"
    )
    parser.add_argument("--branch", type=str, default="main", help="分支名称。默认值：main")
    parser.add_argument("--pattern", type=str, default="*", help="文件匹配模式，使用fnmatch语法。默认值：*")
    parser.add_argument("--commit_message", type=str, default="添加文件", help='提交信息。默认值："添加文件"')
    parser.add_argument("--chunk_size", type=int, default=5 * 1024 * 1024, help="文件块大小（字节）。默认值：5MB")
    parser.add_argument("--retries", type=int, default=3, help="失败重试次数。默认值：3")
    parser.add_argument("--timeout", type=int, default=None, help="超时时间（秒）。默认值：None（永不超时）")
    parser.add_argument("--repo_dir", type=str, default=None, help="远程仓库目录。默认值：None（上传到仓库根目录），如果file_path，此参数无效")
    parser.add_argument("--use_git", action="store_true", help="使用 git 上传。")

    args = parser.parse_args()

    if args.use_git:
        upload_with_git(
            access_token=args.access_token,
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            local_dir=args.file_path,
            branch=args.branch,
            pattern=args.pattern,
            commit_message=args.commit_message,
        )
    else:
        if os.path.isdir(args.file_path):
            push_to_hub(
                dir_path=args.file_path,
                repo_id=args.repo_id,
                repo_type=args.repo_type,
                pattern=args.pattern,
                branch=args.branch,
                commit_message=args.commit_message,
                chunk_size=args.chunk_size,
                retries=args.retries,
                timeout=args.timeout,
            )
        else:
            upload_file(
                file_path=args.file_path,
                repo_id=args.repo_id,
                repo_type=args.repo_type,
                branch=args.branch,
                commit_message=args.commit_message,
                chunk_size=args.chunk_size,
                retries=args.retries,
                timeout=args.timeout,
                repo_dir=args.repo_dir,
            )


if __name__ == "__main__":
    wm_upload()
