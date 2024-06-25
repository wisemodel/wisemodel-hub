import subprocess


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
    subprocess.run([''])
    pass


if __name__ == '__main__':
    repo_id = 'CUHK-DVLab/Mini-Gemini-2B'

    upload("a.model", repo_id)
