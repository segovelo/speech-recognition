import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


def ask_bot(prompt):
    return "This is my answer"

    # prompt = "What is your favorite color?"
    res = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
    )
    # print(res)
    return res["choices"][0]["text"]
