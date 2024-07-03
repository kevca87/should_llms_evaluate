# Make a GET request to the GitHub API
import requests

def get_commit_info(request_url):
  response = requests.get(request_url)
  if response.status_code == 200:
    return response.json()
  else:
    return None