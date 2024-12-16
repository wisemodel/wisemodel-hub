# wisemodel-hub Documentation
这是`wisemodel`开源社区仓库上传和下载工具，用于上传下载数据集、模型、代码等。

## 安装
### 安装依赖
因为目前只发布到了`test pypi`环境，因此有的依赖包测试环境可能没有，需要先手动安装。
```shell
git clone https://github.com/wisemodel/wisemodel-hub
cd wisemodel-hub
pip install -r requirements.txt
```
### 安装`wisemodel-hub`包
```shell
pip install --index-url https://test.pypi.org/simple/ wisemodel_hub
```

## 相关信息
### 仓库id(`repo_id`) 和 仓库类型(`repo_type`)
如果您在主站进入了某个仓库的页面，那么`repo_id`和`repo_type`就在url中。
url的格式如下：
https://www.wisemodel.cn/{repo_type}/{repo_id}

repo_id的格式为：`{account_name}`/`{repo_name}`
其中：`account_name`是仓库主人的用户名，`repo_name`是仓库的名称。


### git token
在主站登录后，进入 https://www.wisemodel.cn/my-token 页面，
在右侧内容区 `git token` 页内获取。

### 本地缓存目录
如果调用函数时不指定`local_dir`, 会下载到本地环境目录，位置在：
`{user_home}`/.cache/wisemodel_hub/`{username}`_`{repo_name}`

## 登录
在登录前需要先注册账号，注册地址为：[https://wisemodel.cn/home](https://wisemodel.cn/home)

在执行需要登录才能执行的函数时，会自动判断是否需要登录，使用用户名和密码进行登录。

当使用notebook时，会退出现流程，并出现登录表单，登录后重新执行原流程即可。

当使用命令行时，会等待用户输入用户名和密码，登录后会继续执行原流程代码。

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

file_path = "/local/file/path"  # 必填
repo_id = "your_repo_id"        # 必填
repo_type = "your_repo_type"    # 库类型，取值范围：models, datasets, codes。可选：默认值 models
branch = "main"                 # your branch name.                        可选：默认值 main
commit_message = "your message" # commit message.                          可选：默认值 "添加文件"
chunk_size = 1024 * 1024        # 设置文件块大小，例如1 MB.                  可选，默认值 5 * 1024 * 1024, 即5MB
retries=3                       # 失败重试次数                              可选，默认值 3
timeout=10                      # 超时时间，如果不设置则一直等待.             可选，默认值 None (永不超时)
repo_dir=None                   # 仓库目录，如果不设置则下载到仓库根目录。     可选，默认值 None

upload_file(file_path, repo_id, repo_type, branch=branch, commit_message=commit_message, chunk_size=chunk_size, retries=retries, timeout=timeout, repo_dir=repo_dir)
``` 

### 上传目录
```python
from wisemodel_hub import push_to_hub

dir_path = "/local/dir/path"    # 必填
repo_id = "your_repo_id"        # 必填
repo_type = "your_repo_type"    # 库类型，取值范围：models, datasets, codes   # 可选，默认值 models
pattern = "*"                   # fnmatch格式的匹配字符串，用于过滤文件名      # 可选，默认为None，即不过滤
branch = "main"                 # your branch name                          # 可选，默认值 main
commit_message = "your message" # commit message                            # 可选，默认值 "上传文件夹"
chunk_size = 1024 * 1024        # 设置文件块大小，例如1 MB                    # 可选，默认值 5 * 1024 * 1024, 即5MB
retries=3                       # 失败重试次数                               # 可选，默认值 3
timeout=10                      # 超时时间，如果不设置则一直等待               # 可选，默认值 None (永不超时)

push_to_hub(dir_path, repo_id, repo_type, pattern=pattern, branch=branch, commit_message=commit_message, chunk_size=chunk_size, retries=3, timeout=10)
``` 

### 利用本地git工具上传
需要本地事先安装`git`和`git-lfs`工具。
整库操作时会更加方便，认证方式与其他两个接口不同。
```python
from wisemodel_hub import upload_with_git

access_token = "your_access_token"           # 必填
repo_id = "your_account/your_repo_name"      # 必填
repo_type = "codes"                          # datasets, models, or codes   # 可选，默认值 models
local_dir = "your_local_dir"                 # 或者替换为目标目录             # 可选，默认为None，即下载到缓存
branch= "main"                               # 或者替换为具体的分支名称       # 可选，默认值 main
#pattern = '*.json'         # fnmatch格式的匹配字符串，用于过滤文件名          # 可选，默认为None，即不过滤
pattern = None                          
commit_message = "upload files"                                              # 可选，默认值 "upload files"

upload_with_git(access_token, repo_id, repo_type, local_dir, branch=branch, pattern=pattern, commit_message=commit_message)
```

## 下载
目前不支持私有项目下载。
### 下载单个文件
单线程下载。
```python
from wisemodel_hub import file_download

repo_id = "your_account/your_repo_name"    # 指定仓库id      # 必填
file_name = "your_file_name"        # 要下载的文件名称        # 必填
repo_type = "models"                # 仓库类型，可选值：'models'、'datasets'、'codes'   # 可选，默认值 models
local_dir = "/local/download/dir"   # 指定本地下载目录，如果为None，则只存储在缓存中 # 可选，默认值 None
branch = "your_branch"              # 指定下载的版本，默认为"main"                 # 可选，默认值 main
force_download = True               # 是否强制下载                                # 可选，默认值 False

file_download(repo_id, file_name, repo_type=repo_type, local_dir=local_dir, branch=branch, force_download=force_download)  
``` 
### 下载单个大文件
并行下载大文件，可以提高下载速度。
```python
from wisemodel_hub import lfs_file_download

repo_id = "your_account/your_repo_name"    # 指定仓库id           # 必填
file_name = "your_file_name"        # 要下载的文件名称             # 必填
repo_type = "models"                # 仓库类型，可选值：'models'、'datasets'、'codes' # 可选，默认值 models
local_dir = "/local/download/dir"   # 指定本地下载目录，如果为None，则只存储在缓存中   # 可选，默认值 None
branch = "your_revision"            # 指定下载的版本，默认为"main"                   # 可选，默认值 main    
num_parts = 8                       # 并行下载线程数                                # 可选，默认值 8
force_download = True               # 是否强制下载                                  # 可选，默认值 False

lfs_file_download(repo_id, file_name, repo_type=repo_type, local_dir=local_dir, branch=branch, num_parts=num_parts, force_download=force_download)

``` 
### 下载目录
将主站整库下载到本地。
``` python
from wisemodel_hub import snapshot_download

repo_id = "your_account/your_repo_name"    # 指定仓库id                              # 必填
repo_type = "models"                # 仓库类型，可选值：'models'、'datasets'、'codes' # 可选，默认值 models
local_dir = "/local/download/dir"   # 指定本地下载目录，如果为None，则只存储在缓存中    # 可选，默认值 None
branch = "your_branch"          # 指定下载分支                                   # 可选，默认值 main
pattern = "*"                       # fnmatch格式的匹配字符串，用于过滤文件名          # 可选，默认为None，即不过滤
num_parts = 8                       # 并行下载线程数                                 # 可选，默认值 8
force_download = True               # 是否强制下载                                   # 可选，默认值 False

snpshot_download(repo_id, repo_type=repo_type, local_dir=local_dir, branch=branch, pattern=pattern, num_parts=num_parts, force_download=force_download)
```

### 利用本地git工具下载
需要本地事先安装`git`和`git-lfs`工具。
整库操作时会更加方便，认证方式与另外三个接口不同。
```python
from wisemodel_hub import download_with_git

access_token = "your_access_token"                       # 必填
repo_id = "your_account/your_repo_name"                 # 必填
repo_type = "codes"                                     # 可选，默认值 models
#pattern = "*.json"          # fnmatch格式的匹配字符串   # 可选，默认为None，即不过滤
#pattern = "constants.py"    
pattern = None
local_dir = "your_local_dir" # 或者替换为目标目录        # 可选，默认为None，即下载到缓存
branch = "main"  # 或者替换为具体的分支名称              # 可选，默认值 main

download_with_git(access_token, repo_id, repo_type=repo_type, pattern=pattern, local_dir=local_dir, branch=branch)
```

## 命令行脚本
在使用`pip`命令安装后`wisemodel_hub`包后，会自动安装命令行脚本，可以直接在命令行中使用。

### 上传脚本
```shell
# 上传目录至远程仓库
wm_upload /local/dir/path your_account/your_repo_name
```

参数说明，使用时在命令输入`wm_upload -h`查看：
```shell
wm_upload -h

usage: wm_upload [-h] [--repo_type REPO_TYPE] [--branch BRANCH] [--commit_message COMMIT_MESSAGE]
                 [--chunk_size CHUNK_SIZE] [--retries RETRIES] [--timeout TIMEOUT] [--repo_dir REPO_DIR] [--use_git]
                 file_path repo_id

上传文件或目录到 wisemodel hub。如果提示输入用户名和密码，请输入登录wisemodel.cn的用户名和密码。

positional arguments:
  file_path             要上传的文件或目录路径。必填
  repo_id               仓库 ID。必填

options:
  -h, --help            show this help message and exit
  --repo_type REPO_TYPE
                        仓库类型（models, datasets, codes）。默认值：models
  --branch BRANCH       分支名称。默认值：main
  --commit_message COMMIT_MESSAGE
                        提交信息。默认值："添加文件"
  --chunk_size CHUNK_SIZE
                        文件块大小（字节）。默认值：5MB
  --retries RETRIES     失败重试次数。默认值：3
  --timeout TIMEOUT     超时时间（秒）。默认值：None（永不超时）
  --repo_dir REPO_DIR   远程仓库目录。默认值：None（上传到仓库根目录），如果参数 file_path 是文件，则起作用，如果参数 file_path 是目录，则无效。
  --use_git             使用 git 上传。
```

### 下载脚本
```shell
# 下载仓库本地缓存
wm_download your_account/your_repo_name
```

参数说明，使用时在命令输入`wm_download -h`查看：
```shell
wm_download -h

usage: wm_download [-h] [--file_name [FILE_NAME]] [--repo_type REPO_TYPE] [--local_dir LOCAL_DIR] [--branch BRANCH]
                   [--num_parts NUM_PARTS] [--force_download] [--pattern PATTERN] [--use_git]
                   [--access_token ACCESS_TOKEN]
                   repo_id

从 wisemodel hub 下载文件或目录。如果提示输入用户名和密码，请输入登录wisemodel.cn的用户名和密码。

positional arguments:
  repo_id               仓库 ID。必填

options:
  -h, --help            show this help message and exit
  --file_name [FILE_NAME]
                        要下载的文件名（若下载目录则留空）。
  --repo_type REPO_TYPE
                        仓库类型（models, datasets, codes）。默认值：models
  --local_dir LOCAL_DIR
                        本地下载目录。默认值：None
  --branch BRANCH       分支名称。默认值：main
  --num_parts NUM_PARTS
                        并行下载线程数。默认值：1。设置值超过1 则使用分块下载
  --force_download      强制下载。默认值：False
  --pattern PATTERN     用于过滤文件名的匹配字符串。默认值：None
  --use_git             使用 git 下载。默认值：False。如果使用git，则必须提供 access_token
  --access_token ACCESS_TOKEN
                        请到主站->用户中心->Token与Key 页面中查找。
```