import os

WM_ENDPOINT = 'https://awsdownload.wisemodel.cn'
WM_GITLAB_ENDPOINT = 'https://wisemodel.cn'
REVISION = 'main'
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".cache", "wisemodel")
RETRY_TIMES = 3