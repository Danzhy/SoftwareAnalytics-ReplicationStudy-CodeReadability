import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = '../../datasets/Selected Merged PRs with code readabiliy improvements.csv'
OUTPUT_BASE = '../../outputs/beforeandafter'
GITHUB_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN", "") 
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def parse_github_url(url):

    parts = str(url).strip().split('/')
    owner = parts[3]
    repo = parts[4]
    sha_after = parts[-1]
    return owner, repo, sha_after

def get_parent_sha(owner, repo, sha_after):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha_after}"
    response = requests.get(api_url, headers=HEADERS, timeout=15)
    if response.status_code == 200:
        data = response.json()
        return data['parents'][0]['sha'], None
    return None, f"API Error: {response.status_code}"

def download_file(url, target_path):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return True, None
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    print(f"Error: {CSV_PATH} not found.")
    exit()

for i, row in df.iterrows():
    folder_num = i + 2  
    
    if folder_num > 402: 
        break
    
    folder_path = os.path.join(OUTPUT_BASE, str(folder_num))
    error_log = os.path.join(folder_path, 'error.txt')
    
    if os.path.exists(folder_path) and not os.path.exists(error_log):
        print(f"Skipping folder {folder_num} (Already processed)")
        continue

    os.makedirs(folder_path, exist_ok=True)

    try:
        full_commit_url = row['Pull Request - Commit URL']
        file_path = row['Class']
        
        owner, repo_name, commit_after = parse_github_url(full_commit_url)
        
        print(f"Processing folder {folder_num} ({repo_name})...")

        commit_before, api_err = get_parent_sha(owner, repo_name, commit_after)
        
        if not commit_before:
            raise Exception(api_err)

        raw_base = f"https://raw.githubusercontent.com/{owner}/{repo_name}"
        url_before = f"{raw_base}/{commit_before}/{file_path}"
        url_after = f"{raw_base}/{commit_after}/{file_path}"

        path_before = os.path.join(folder_path, 'before', os.path.basename(file_path))
        path_after = os.path.join(folder_path, 'after', os.path.basename(file_path))

        success_b, err_b = download_file(url_before, path_before)
        success_a, err_a = download_file(url_after, path_after)

        if not success_b or not success_a:
            with open(error_log, 'w') as f:
                f.write(f"Before Error: {err_b}\nAfter Error: {err_a}\nURL After: {url_after}")
            print(f"  [X] Failed folder {folder_num}")
        else:
            if os.path.exists(error_log):
                os.remove(error_log)
            print(f"  [✓] Success folder {folder_num}")

    except Exception as e:
        with open(error_log, 'w') as f:
            f.write(f"Process Error: {str(e)}")
        print(f"  [X] Failed folder {folder_num}: {e}")
    
    time.sleep(0.5)