from llm import LLM
import os
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 
import requests
import json

class Codestral(LLM):
    def __init__(self):
        super().__init__()
        self.name = "codestral-latest"
        self.api_key = os.getenv("MISTRAL_API_KEY")

    def instruct(self, instruction):
        self.instruction = instruction

    def get_instruction(self):
        return self.instruction

    def request_api(self, data):
        url = "https://codestral.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
    def evaluate_sample(self, sample):
        messages = [
            {"role": "system", "content": self.get_instruction()},
            {"role": "user", "content": sample}
        ]
        data = {
            "model": self.name,
            "messages": messages,
            "response_format": {
                "type": "json_object"
            },
            "temperature": 0.0,
            # "top_p": 1,
            # "max_tokens": 512,
            # "stream": false,
            # "safe_prompt": false,
            # "random_seed": 1337
        }
        try:
            response = self.request_api(data)
            instruct_answer = json.loads(response['choices'][0]['message']['content'])
            assert "answer" in instruct_answer
            assert "explanation" in instruct_answer
            return instruct_answer
        except Exception as e:
            return {"answer": None, "explanation": f"{e}"}

        

        