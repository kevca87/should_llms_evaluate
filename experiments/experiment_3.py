import pandas as pd
from llm import LLM
from codestral import Codestral
from github_api import get_commit_info
from time import sleep
import numpy as np

def get_models():
    models = [Codestral()]
    return models

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

def evaluate_commit(model, commit_record):
    api_url = url_to_api_url(commit_record['url'])
    commit_diff = get_commit_diff(api_url)
    commit_sample = f"MESSAGE: {commit_record['message']}\nDIFF: {commit_diff}"
    model_answer = model.evaluate_sample(commit_sample)
    return model_answer

def evaluate_commits_with_instruction(model, commits, instruction):
    model.instruct(instruction['instruction'])
    total = len(commits)
    commits[instruction['answer_column_name']] = pd.Series(dtype='str')
    commits[instruction['explanation_column_name']] = pd.Series(dtype='str')
    for idx, commit in commits.iterrows():
        model_answer = evaluate_commit(model, commit)
        commits.loc[idx,instruction['answer_column_name']] = model_answer['answer']
        commits.loc[idx,instruction['explanation_column_name']] = model_answer['explanation']
        print(f'Progress: {idx+1}/{total}',end='\r')
        commits.to_csv(f'../results/cm_what_and_why_{model.name}.csv', index=False) # Commit Message Evaluation
        sleep(2)
    return  commits


def get_instructions():
    file_name = "../prompts/instructions_what_and_why.xlsx"
    df = pd.read_excel(file_name)
    df['answer_column_name'] = df['category']
    df['explanation_column_name'] = df['category'] + '_expl'
    return df

def get_commits():
    file_name = "../data/sampled messages.csv"
    df = pd.read_csv(file_name)
    return df

if __name__ == '__main__':
    commits = get_commits()
    models = get_models()
    contains_whys = []
    explanations = []
    instructions = get_instructions()
    for model in models:
        for idx, instruction in instructions.iterrows():
            # print (f'Instruction {instruction["category"]}')
            commits = evaluate_commits_with_instruction(model, commits, instruction)
    commits.to_csv(f'../results/cm_what_and_why_{model.name}.csv', index=False) # Commit Message Evaluation