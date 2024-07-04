import pandas as pd
from llm import LLM
from codestral import Codestral
from github_api import get_commit_info
from time import sleep
import numpy as np

def get_models():
    models = [Codestral()]
    return models

def evaluate_commit(model, commit_record):
    commit_diff = commit_record['diff']
    commit_sample = f"MESSAGE: {commit_record['message']}\nDIFF: {commit_diff}"
    model_answer = model.evaluate_sample(commit_sample)
    return model_answer

def evaluate_commits_with_instruction(model, commits, instruction):
    model.instruct(instruction['instruction'])
    total = len(commits)
    column_names = commits.columns.to_list()
    column_names.remove('diff')
    column_names.remove('url')
    column_names.remove('message')
    commits[instruction['answer_column_name']] = pd.Series(dtype='bool')
    commits[instruction['explanation_column_name']] = pd.Series(dtype='str')
    for idx, commit in commits.iterrows():
        model_answer = evaluate_commit(model, commit)
        commits.loc[idx,instruction['answer_column_name']] = model_answer['answer']
        commits.loc[idx,instruction['explanation_column_name']] = model_answer['explanation']
        print(f'Progress: {idx+1}/{total}',end='\r')
        commits.to_csv(f'./cme_{model.name}.csv', index=False, columns=column_names) # Commit Message Evaluation
        sleep(1.8)
    return  commits

def get_instructions():
    file_name = "./data/category_instructions.xlsx"
    df = pd.read_excel(file_name)
    df['answer_column_name'] = df['category']
    df['explanation_column_name'] = df['category'] + '_expl'
    return df

def get_commits():
    file_name = "./commits.csv"
    # file_name = "./data/sampled messages.csv"
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
            print (f'Instruction {instruction["category"]}')
            commits = evaluate_commits_with_instruction(model, commits, instruction)
    commits.to_csv(f'./cme_{model.name}_finished.csv', index=False) # Commit Message Evaluation

# Rate limit 30 per minute and 2000 per day
# https://docs.mistral.ai/capabilities/code_generation/

# TODO:
# - Improve prompt with the definition and implicit cases of "Why the changes are needed?"
# - Save contains 
# - Save explanation
# - Save commit diff?
# - Check parameters api