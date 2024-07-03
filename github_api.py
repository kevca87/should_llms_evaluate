# Make a GET request to the GitHub API
import requests

def get_commit_info(request_url):
  headers = {
    "Authorization": f"token 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",
    "Content-Type": "application/json",
    "Accept": "application/json"
  }
  response = requests.get(request_url, headers=headers)
  if response.status_code == 200:
    return response.json()
  else:
    return None