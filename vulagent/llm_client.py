import os

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class LLMClient:
    def __init__(self, temperature=0.0):
        self.client = OpenAI(
            base_url=os.getenv("API_URL"),
            api_key=os.getenv("API_KEY"))
        self.model = os.getenv("LLM_MODEL")
        self.temperature = temperature

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content
