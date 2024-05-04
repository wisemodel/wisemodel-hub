import gitlab
from contants import WM_GITLAB_ENDPOINT

#Get file names from GitLab repo based on repo id
def get_file_names(repo_id):
    gl = gitlab.Gitlab(WM_GITLAB_ENDPOINT)
    project = gl.projects.get(repo_id)
    files = project.repository_tree()
    return [file['name'] for file in files if file['type'] == 'blob']

if __name__ == '__main__':
    repo_id = '01.AI/Yi-34B-Chat-4bits'
    file_names = get_file_names(repo_id)
    for file_name in file_names:
        print(file_name)
