import os
import time

import requests
import sys
from tqdm import tqdm

SERVER_URL = "http://47.244.38.108:5001/upload"


def upload_chunks(file_path, chunk_data, chunk_index, total_chunks, repo_id, token, commit, url):
    file_name = os.path.basename(file_path)

    headers = {
        'Content-Type': 'application/octet-stream',
        'X-Token': token,
        'X-RepoId': repo_id,
        'X-Commit': commit,
        'X-AuthToken': '49c04086-41ac-11ef-af16-4e438d67654a',
        'X-File-Name': file_name,
        'X-Chunk-Index': str(chunk_index),
        'X-Total-Chunks': str(total_chunks)
    }
    response = requests.post(url, data=chunk_data, headers=headers)
    print(f"Chunk {chunk_index + 1}/{total_chunks} uploaded. Status code: {response.status_code}")


def upload_with_progress_bar(file_path, repo_id, token, commit, url=SERVER_URL, chunk_size=20 * 1024 * 1024):
    file_size = os.path.getsize(file_path)
    num_chunks = (file_size + chunk_size - 1) // chunk_size
    chunk_index = 0
    with open(file_path, 'rb') as file, tqdm(total=file_size, unit='B', unit_scale=True, desc=file_path) as pbar:
        chunk = file.read(chunk_size)
        while chunk:
            if chunk_index == num_chunks - 1:
                print("最后一包处理耗时可能较长，请耐心等待......")
            upload_chunks(file_path, chunk, chunk_index, num_chunks, repo_id, token, commit, url)  # 注意这里只发送当前块
            pbar.update(len(chunk))
            chunk = file.read(chunk_size)
            chunk_index += 1
    print("文件：{} 上传成功！请查看仓库目录".format(file_path))


if __name__ == '__main__':
    # upload_with_progress_bar("/home/www/wisemodel-test/test_model_hub/64-8bits.3.tflite", "http://127.0.0.1:5001/upload", "AIMODELL/test_model_hub", "wisemodel-8M2T9S2JjiMHh6vqxoQh", "commit content")

    argv = sys.argv
    if len(argv) < 4:
        print('Usage: {} file_path token repo [commit] ...'.format(argv[0]))
        sys.exit(1)

    filepath = sys.argv[1]
    print("filepath: {}".format(filepath))
    # file_path = '/path/to/your/local/file.txt'
    # url = 'http://localhost:5001/upload'
    # cur_timestamp = int(time.time())

    token = sys.argv[2]
    repo_id = sys.argv[3]
    commit = ""
    if len(argv) >= 5:
        commit = sys.argv[4]
    upload_with_progress_bar(filepath, repo_id, token, commit)
