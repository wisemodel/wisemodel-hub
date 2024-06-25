import subprocess

wisemodel_repo_url = "https://oauth2:%s@www.wisemodel.cn/%s/%s.git"
token = "wisemodel-8M2T9S2JjiMHh6vqxoQh"

def upload(filename, repo_id):
    result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
    print(result.stdout)
    print("step1: install git..")
    print("step2: install git lfs..")
    subprocess.run(['curl', '-s', 'https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh'])
    print('download complete.')
    subprocess.run(['bash', 'script.rpm.sh'])
    print('install repo')
    subprocess.run(['yum', '-y', 'install', 'git-lfs'])
    print('install git lfs success')
    subprocess.run(['git', 'lfs', 'install'])
    print('git lfs initialized!')
    git_repo_url = wisemodel_repo_url.format(token, 'AIMODELL', 'test_model_hub')
    print('git repo url' + git_repo_url)
    subprocess.run(['git', 'clone', wisemodel_repo_url])
    print('git project clone complete')
    subprocess.run(['cd', './test_model_hub'])
    print('cd project dir.')
    subprocess.run(['touch', 'a.bin'])
    print('mock a model file')
    subprocess.run(['git', 'add', 'a.bin'])
    print('git add')
    subprocess.run(['git', 'commit', 'upload file'])
    print('git commit')
    subprocess.run(['git', 'push'])
    print('git push')

    pass


if __name__ == '__main__':
    repo_id = 'CUHK-DVLab/Mini-Gemini-2B'

    upload("a.model", repo_id)
