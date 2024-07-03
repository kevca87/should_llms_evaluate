import pandas as pd
from llm import LLM
from codestral import Codestral
from github_api import get_commit_info
from time import sleep


def get_models():
    models = [Codestral()]
    return models

def evaluate_commit(model, commit_record):
    commit_diff = commit_record['diff']
    commit_sample = f"MESSAGE: {commit_record['message']}\nDIFF: {commit_diff}"
    model_answer = model.evaluate_sample(commit_sample)
    return model_answer

def evaluate_commits_with_instruction(model, commits, instruction):
    answers = []
    explanations = []
    model.instruct(instruction)
    total = len(commits)
    for idx, commit in commits.iterrows():
        model_answer = evaluate_commit(model, commit)
        answers.append(model_answer['answer'])
        explanations.append(model_answer['explanation'])
        print(f'Progress: {idx+1}/{total}',end='\r')
        sleep(2)
    return  {'answers':answers, 'explanations': explanations}

def get_instructions():
    file_name = "./data/category_instructions.xlsx"
    df = pd.read_excel(file_name)
    df['answer_column_name'] = df['category']
    df['explanation_column_name'] = df['category'] + '_expl'
    return df

def get_commits():
    file_name = "./commits.csv"
    df = pd.read_csv(file_name)
    return df

if __name__ == '__main__':
    commits = get_commits()[:2]
    models = get_models()
    contains_whys = []
    explanations = []
    instructions = get_instructions()
    for model in models:
        for idx, instruction in instructions.iterrows():
            print (f'Instruction {instruction["category"]}')
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