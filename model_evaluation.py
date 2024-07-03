import pandas as pd
from llm import LLM
from codestral import Codestral
from github_api import get_commit_info
from time import sleep

def url_to_api_url(url):
    url_split = url.split('/')
    commit_sha = url_split[-1]
    repo = f'{url_split[-4]}/{url_split[-3]}'
    api_url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
    return api_url

def get_commits():
    file_name = "./sampled messages.csv"
    df = pd.read_csv(file_name)
    df['api_url'] = df['url'].apply(url_to_api_url)
    return df

def get_commit_diff(request_url):
    diff = ''
    changed_files = get_commit_info(request_url)['files']
    for file in changed_files:
        diff += (file['patch'] + '\n')
    return diff

def get_models():
    models = [Codestral()]
    return models

def evaluate_commit(model, commit_record):
    commit_diff = get_commit_diff(commit_record['api_url'])
    commit_sample = f"MESSAGE: {commit_record['message']}\nDIFF: {commit_diff}"
    model_answer = model.evaluate_sample(commit_sample)
    return model_answer

def evaluate_commits_with_instruction(model, commits, instruction):
    answers = []
    explanations = []
    model.instruct(instruction)
    for idx, commit in commits.iterrows():
        print(commit)
        model_answer = evaluate_commit(model, commit)
        answers.append(model_answer['answer'])
        explanations.append(model_answer['explanation'])
        sleep(2)
    return  {'answers':answers, 'explanations': explanations}

if __name__ == '__main__':
    commits = get_commits()[:10]
    print(commits)
    models = get_models()
    contains_whys = []
    explanations = []
    instructions = [
        {
            'answer_column_name':'contains_why',
            'explanation_column_name':'contains_why_expl',
            'instruction':'Given the code and the commit message. Does the following commit message contains "Why the changes are needed? (describe the reasons for the changes)"? Explain your decision. Answer in JSON format.\n{ "answer":true/false,\n"explanation":"For example: The first part of the message refers that the fix is needed for improve the performance"\n}'
        },
        {
            'answer_column_name':'contains_what',
            'explanation_column_name':'contains_what_expl',
            'instruction':'Given the code and the commit message. Does the following commit message contains "What was changed? (summarize the changes in this commit)"? Explain your decision. Answer in JSON format.\n{ "answer":true/false,\n"explanation":"For example: The first part of the message refers that the fix is needed for improve the performance"\n}'
        }
    ]
    for model in models:
        for instruction in instructions:
            results = evaluate_commits_with_instruction(model, commits, instruction['instruction'])
            commits[instruction['answer_column_name']] = results['answers']
            commits[instruction['explanation_column_name']] = results['explanations']
        commits.to_csv(f'./cme_{model.name}.csv', index=False) # Commit Message Evaluation
        

# Rate limit 30 per minute and 2000 per day
# https://docs.mistral.ai/capabilities/code_generation/

# TODO:
# - Improve prompt with the definition and implicit cases of "Why the changes are needed?"
# - Save contains 
# - Save explanation
# - Save commit diff?
# - Check parameters api