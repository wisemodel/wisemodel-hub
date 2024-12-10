# wisemodel-hub README
这是wisemodel开源社区仓库上传和下载工具，用于上传下载数据集、模型、代码等。

## 安装
```shell
pip install --index-url https://test.pypi.org/simple/ wisemodel_hub
```

## 相关信息获取
### 仓库id(`repo_id`) 和 仓库类型(`repo_type`)
如果您在主站进入了某个仓库的页面，那么repo_id和repo_type就在url中。
url的格式如下：
https://www.wisemodel.cn/{repo_type}/{repo_id}

repo_id的格式为：{account_name}/{repo_name}
其中：account_name是仓库主人的用户名，repo_name是仓库的名称。


### git token
在主站登录后，进入 https://www.wisemodel.cn/my-token 页面，
在右侧内容区 `git token` 页内获取。

## 登录
在登录前需要先注册账号，注册地址为：[https://wisemodel.cn/home](https://wisemodel.cn/home)

### 自动登录
在执行需要登录才能执行的函数时，会自动判断是否需要登录，使用用户名和密码进行登录。
当使用notebook时，登录后重新执行原流程即可。
当使用命令行时，登录后会自动执行原流程代码。

### notebook登录
```python
from wisemodel_hub import notebook_login

notebook_login(new_session=True)
```

### 命令行登录
```python
from wisemodel_hub import login

login(new_session=True)
```

## 上传
### 上传单个文件
```python
from wisemodel_hub import upload_file

file_path = "/local/file/path"
repo_id = "your_repo_id"
repo_type = "your_repo_type"                  # 库类型，取值范围：models, datasets, codes
branch = "main"                 # your branch name
commit_message = "your message" # commit message
chunk_size = 1024 * 1024        # 设置文件块大小，例如1 MB
retries=3                       # 失败重试次数
timeout=10                      # 超时时间，如果不设置则一直等待

upload_file(file_path, repo_id, repo_type, branch=branch, commit_message=commit_message, chunk_size=chunk_size, retries=retries, timeout=timeout)
``` 

### 上传目录
```python
from wisemodel_hub import push_to_hub

dir_path = "/local/dir/path"
repo_id = "your_repo_id"
repo_type = "your_repo_type"    # 库类型，取值范围：models, datasets, codes
regex_pattern = "*"             # 匹配上传文件名的正则表达式，例如"*.py"
branch = "main"                 # your branch name
commit_message = "your message" # commit message
chunk_size = 1024 * 1024        # 设置文件块大小，例如1 MB
retries=3                       # 失败重试次数
timeout=10                      # 超时时间，如果不设置则一直等待

push_to_hub(dir_path, repo_id, repo_type, regex_pattern=regex_pattern, branch=branch, commit_message=commit_message, chunk_size=chunk_size, retries=3, timeout=10)
``` 

### 利用本地git工具上传
适用库内有文件夹的情况
```python
from wisemodel_hub import upload_with_git

access_token = "your_access_token" # 在主站登录后，在https://www.wisemodel.cn/my-token 页面中，`git token`tab页内获取
repo_id = "your_account/your_repo_name"
repo_type = "codes"     # datasets, models, or codes
local_dir = "your_local_dir" # 或者替换为目标目录
branch= "main"  # 或者替换为具体的分支名称
#pattern = r'.*\.(log|txt|json)$'    # 或者替换为正则表达式或具体文件名
pattern = None
commit_message = "upload files"

upload_with_git(access_token, repo_id, repo_type, local_dir, branch=branch, pattern=pattern, commit_message=commit_message)
```

## 下载
目前不支持私有项目下载。
### 下载单个文件
单线程下载。
```python
from wisemodel_hub import file_download

repo_id = "your_account/your_repo_name"    # 指定仓库id
file_name = "your_file_name"        # 要下载的文件名称
local_dir = "/local/download/dir"   # 指定本地下载目录，如果为None，则只存储在缓存中
revision = "your_revision"          # 指定下载的版本，默认为"main"
force_download = True               # 是否强制下载，如果为True，则会重新下载文件，即使本地存在该文件

file_download(repo_id, file_name, local_dir=local_dir, revision="main", force_download=force_download)  
``` 
### 下载单个大文件
并行下载大文件，可以提高下载速度。
```python
from wisemodel_hub import lfs_file_download

repo_id = "your_account/your_repo_name"    # 指定仓库id
file_name = "your_file_name"        # 要下载的文件名称
local_dir = "/local/download/dir"   # 指定本地下载目录，如果为None，则只存储在缓存中
revision = "your_revision"          # 指定下载的版本，默认为"main"
num_parts = 8                       # 并行下载线程数
force_download = True               # 是否强制下载，如果为True，则会重新下载文件，即使本地存在该文件

lfs_file_download(repo_id, file_name, local_dir=local_dir, revision="main", num_parts=num_parts, force_download=force_download)

``` 
### 下载目录
将主站整库下载到本地。
``` python
from wisemodel_hub import snapshot_download

repo_id = "your_account/your_repo_name"    # 指定仓库id
local_dir = "/local/download/dir"   # 指定本地下载目录，如果为None，则只存储在缓存中
revision = "your_revision"          # 指定下载版本，默认为"main"
regex_pattern = "*"                 # 匹配下载文件名的正则表达式，例如"*.py"
num_parts = 8                       # 并行下载线程数
force_download = True               # 是否强制下载，如果为True，则会重新下载文件，即使本地存在该文件

snpshot_download(repo_id, local_dir=local_dir, revision="main", regex_pattern=regex_pattern, num_parts=num_parts, force_download=force_download)
```

### 利用本地git工具下载
适用库内有文件夹的情况
```python
from wisemodel_hub import download_with_git

access_token = "your_access_token"
repo_id = "your_account/your_repo_name"
repo_type = "codes"
#pattern = r".*\.json$"    # 或者替换为正则表达式或具体文件名
#pattern = r"^constants\.py$"    # 或者替换为正则表达式或具体文件名
pattern = None
local_dir = "your_local_dir" # 或者替换为目标目录
branch = "main"  # 或者替换为具体的分支名称

download_with_git(access_token, repo_id, repo_type=repo_type, pattern=pattern, local_dir=local_dir, branch=branch)
```