import subprocess

def upload(filename, repo_id):
    result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
    print(result.stdout)
    pass

if __name__ == '__main__':
    repo_id = 'CUHK-DVLab/Mini-Gemini-2B'

    upload("a.model", repo_id)
