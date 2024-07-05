from openai import OpenAI
import pandas as pd
from github_api import get_commit_info

client = OpenAI(api_key="OPENAI-TOKEN")

def get_prompt():
    # Preguntar solo por la clasificacion
    # Posible approach preguntar solo por la existencia
    prompt = 'Given the code and the commit message. Does the following commit message contains "Why the changes are needed? (describe the reasons for the changes)"? Explain your decision. Answer in JSON format.\n{ "containsWhy":"yes",\n"explanation":"The first part of the message refers that the fix is needed for improve the performance"\n}'
    return prompt

def get_commit_diff(request_url):
    diff = ''
    changed_files = get_commit_info(request_url)['files']
    for file in changed_files:
        diff += (file['patch'] + '\n')
    return diff

file_name = "./sampled messages.csv"
df = pd.read_csv(file_name)
commit_message = df['message'][0]
# print(df['message'][0])
# print(df['label'][0])
# print(df['url'][0])
url = df['url'][0]
url_split = url.split('/')
commit_sha = url_split[-1]
repo = f'{url_split[-4]}/{url_split[-3]}'
request_url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
# print(request_url)
# print(get_commit_diff(request_url))
# https://api.github.com/repos/voluntio-bo/website/commits/978771bcc0635c8577a08519a5377ba56de02868

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": get_prompt()},
    {"role": "user", "content": f'MESSAGE: {commit_message}\nDIFF: {get_commit_diff(request_url)}'}
  ]
)

print(completion.choices[0].message)
# ChatCompletionMessage(content='{\n  "containsWhy": "no",\n  "explanation": "The commit message provides details of the changes made in the code to mark ThreadGroups as daemon groups and prevent race conditions. However, it does not explicitly mention the reasons behind the changes. The message mainly focuses on what was changed and the potential issues that were fixed."\n}', role='assistant', function_call=None, tool_calls=None)

# https://github.com/sahil280114/codealpaca
# https://mistral.ai/
# https://huggingface.co/Salesforce/instructcodet5p-16b
