import functools
import getpass
import json
import logging
import os

import requests

from .constants import CACHE_PATH, NOTEBOOK_LOGIN_HTML_END, NOTEBOOK_LOGIN_HTML_START, WM_URL_LOGIN


logger = logging.getLogger(__name__)


def _login_with_url(username, password):
    token_file_path = os.path.join(CACHE_PATH, ".token")
    # 请求获取 token
    payload = {"username": username, "password": password, "way": "normal"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(WM_URL_LOGIN, data=json.dumps(payload), headers=headers)
    response_data = response.json()

    if response_data["code"] == 0:
        token = response_data["data"]["token"]
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        if os.path.exists(token_file_path):
            os.remove(token_file_path)
        with open(token_file_path, "w") as token_file:
            token_file.write(token)
        logger.info(f"Login success with token: {token}")
    else:
        raise Exception(f"Failed to login: {response_data['message']}")


def get_local_token():
    """
    get_local_token 获取缓存中的token
    -----------------------------------

    从缓存获取api token

    返回值：
    ::::::::::
        str: api token
    """
    token_file_path = os.path.join(CACHE_PATH, ".token")

    # 检查本地是否已有 token 文件
    if os.path.exists(token_file_path):
        with open(token_file_path, "r") as token_file:
            token = token_file.read().strip()
            if token:
                return token

    return None


def notebook_login(new_session=False):
    """
    notebook_login 获取主站api访问token
    -----------------------------------

    登录到 WiseModel Hub 并获取 token

    参数：
    ::::::::::
        - **new_session** (bool, optional) - 是否使用新的会话登录. Defaults to False.
    """
    # 检查本地是否已有 token 文件
    if not new_session:
        token = get_local_token()
        if token:
            logger.info(
                "User is already logged in. If you want to login with a different account, invoke notebook_login() or login() function, and set `new_session=True`"
            )
            return

    try:
        import ipywidgets.widgets as widgets  # type: ignore
        from IPython.display import display  # type: ignore
    except ImportError:
        raise ImportError(
            "The `notebook_login` function can only be used in a notebook (Jupyter or"
            " Colab) and you need the `ipywidgets` module: `pip install ipywidgets`."
        )

    box_layout = widgets.Layout(display="flex", flex_flow="column", align_items="center", width="50%")
    username_widget = widgets.Text(description="Username:")
    password_widget = widgets.Password(description="Password:")
    login_button = widgets.Button(description="Login")

    output = widgets.Output()

    login_token_widget = widgets.VBox(
        [
            widgets.HTML(NOTEBOOK_LOGIN_HTML_START),
            username_widget,
            password_widget,
            login_button,
            widgets.HTML(NOTEBOOK_LOGIN_HTML_END),
        ],
        layout=box_layout,
    )
    display(login_token_widget)
    display(output)

    def on_button_clicked(b):
        try:
            _login_with_url(username_widget.value.strip(), password_widget.value.strip())
            with output:
                output.clear_output()
                logger.info("Login success!")
        except Exception as e:
            with output:
                output.clear_output()
                raise Exception(f"Failed to login: {e}")

    login_button.on_click(on_button_clicked)


def login(new_session=False):
    """
    login 获取主站api访问token
    -----------------------------

    登录到 WiseModel Hub 并获取 token

    参数：
    :::::::::::
        - **new_session** (bool, optional) - 是否使用新的会话登录. Defaults to False.
    """
    # 检查本地是否已有 token 文件
    if not new_session:
        token = get_local_token()
        if token:
            logger.info(
                "User is already logged in. If you want to login with a different account, invoke notebook_login() or login() function, and set `new_session=True`"
            )
            return

    username = input("Username: ")
    password = getpass.getpass("Password: ")
    _login_with_url(username, password)
    logger.info("Login success!")


def login_required(func):
    from .utils import is_notebook

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if is_notebook():
            notebook_login()
        else:
            login()
        return func(*args, **kwargs)

    return wrapper
