from github_api import get_commit_info
import pandas as pd
from time import sleep

def get_commits_diffs(commits):
    diffs = []
    for idx, commit in commits.iterrows():
        diffs.append(get_commit_diff(commit['api_url']))
    return diffs

def get_commit_diff(request_url):
    diff = ''
    try:
        changed_files = get_commit_info(request_url)['files']
        sleep(0.1)
        for file in changed_files:
            if 'patch' in file:
                diff += (file['patch'] + '\n')
        return diff
    except:
        return None

def url_to_api_url(url):
    url_split = url.split('/')
    commit_sha = url_split[-1]
    repo = f'{url_split[-4]}/{url_split[-3]}'
    api_url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
    return api_url

def get_commits():
    # file_name = "./sampled messages.csv"
    file_name = "./manual_labeled.csv"
    df = pd.read_csv(file_name)
    df['api_url'] = df['url'].apply(url_to_api_url)
    df['diff'] = get_commits_diffs(df)
    return df

if __name__ == '__main__':
    commits = get_commits()
    commits.to_csv('./commits.csv', index=False)