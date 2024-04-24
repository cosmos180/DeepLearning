'''
Author       : bughero jinxinhou@tuputech.com
Date         : 2023-11-07 19:19:06
LastEditors  : bughero jinxinhou@tuputech.com
LastEditTime : 2023-11-16 11:10:27
FilePath     : /DeepLearning/python/DeepLearningPython/langchain/openai-test.py
Description  : 

Copyright (c) 2023 by Antyme, All Rights Reserved. 
'''
import os
from openai import OpenAI

api_key = "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"

os.environ["OPENAI_PROXY"] = "http://127.0.0.1:7890"
os.environ["OPENAI_API_KEY"] = api_key


client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ]
)

print(completion)
