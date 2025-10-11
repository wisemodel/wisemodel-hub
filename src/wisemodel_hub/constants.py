import os


WM_ENDPOINT = "https://download.wisemodel.cn"
WM_GITLAB_ENDPOINT = "https://wisemodel.cn"
REVISION = "main"
CACHE_PATH = os.path.join(os.path.expanduser("~"), ".cache", "wisemodel")
RETRY_TIMES = 3
HEADERS = {}
HEADERS["Accept"] = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
)
HEADERS["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
HEADERS["Cookie"] = (
    "_ga=GA1.1.1928334475.1726100366; _ga_R1FN4KJKJH=GS1.1.1726100366.1.0.1726100372.0.0.0; ajs_anonymous_id=ec015c9c-f1e5-43a5-ae39-fb6910b8a9e9"
)
TEN_MB = 10 * 1024 * 1024
SLEEP_TIME = 5

WM_URL_BASE = "https://www.wisemodel.cn"
WM_URL_UPLOAD_BASE = "https://uploadfile.wisemodel.cn"
WM_URL_CHECK = f"{WM_URL_UPLOAD_BASE}/gateway/fileupload/api/v1/check"
WM_URL_UPLOAD = f"{WM_URL_UPLOAD_BASE}/gateway/fileupload/api/v1/upload"
WM_URL_MERGE = f"{WM_URL_UPLOAD_BASE}/gateway/fileupload/api/v1/merge"
WM_URL_ADDFILES = f"{WM_URL_UPLOAD_BASE}/gateway/fileupload/api/v1/addfiles"
WM_URL_LOGIN = "https://www.wisemodel.cn/gateway/user/api/v1/login"
WM_URL_LIST_BRANCH = "https://wisemodel.cn/gateway/project/api/v1/branchlist"
WM_URL_LIST_FILES = "https://wisemodel.cn/gateway/project/api/v1/listfiles"

NOTEBOOK_LOGIN_HTML_START = """<center> <img
src=https://www.wisemodel.cn/img/logo.31fb6580.png
alt='Wise Model'> <br> After entering your username and password,
you can log in immediately and then proceed again. If you want to
log in with a different user, please log in again using
notebook_Login (new_dession=True) or login (new_dession=True).
</center>"""
NOTEBOOK_LOGIN_HTML_END = """
<b>Pro Tip:</b> If you don't have an account yet, please create one
on the www.wisemodel.cn </center>"""
