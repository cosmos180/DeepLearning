"""
Author: bughero jinxinhou@tuputech.com
Date: 2023-10-31 18:04:41
LastEditors: bughero jinxinhou@tuputech.com
LastEditTime: 2023-10-31 18:04:54
FilePath: /DeepLearning/python/langchain/HelloLangchain.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

import os

from operator import itemgetter
from langchain.schema.runnable import RunnableLambda
from langchain.llms import OpenAI
# from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser

models = ("gpt-35-turbo", "gpt-35-turbo-16k", "gpt-4",
          "gpt-4-32k", "text-embedding-ada-002")

# llm = ChatOpenAI(
#     model_name="gpt-4-32k",
#     openai_api_base="https://chatserverca.openai.azure.com/",
#     openai_api_key="fd7bdd309896436fa174e401cd41e2fb",
#     temperature=0,
#     max_tokens=3000,
#     verbose=True,
# )

llm = AzureChatOpenAI(deployment_name="gpt-4-32k",
                      openai_api_base="https://chatserverca.openai.azure.com/",
                      openai_api_key="fd7bdd309896436fa174e401cd41e2fb",
                      openai_api_version="2023-06-01-preview",
                      temperature=2.0,
                      verbose=True)
# llm = ChatOpenAI(model_name="gpt-4-1106-preview",
#                  openai_api_base="http://10.22.0.5:9000/v1",
#                  openai_api_key="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",
#                  temperature=0.7,
#                  max_tokens=128*1024,
#                  verbose=True)


# bughero
# os.environ["OPENAI_PROXY"] = "http://127.0.0.1:7890"
# os.environ["OPENAI_API_KEY"] = "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"

# tuputech
# os.environ["OPENAI_API_KEY"] = "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"

# llm = ChatOpenAI(model="gpt-3.5-turbo")
# llm = ChatOpenAI(model="gpt-4")
# llm = OpenAI(client="DevelopA",
#              model="text-davinci-003",
#              temperature=0,
#              max_tokens=4096,
#              verbose=True)


############################## OutputParser ##############################
# class CommaSeparatedListOutputParser(BaseOutputParser):
#     """Parse the output of an LLM call to a comma-separated list."""

#     def parse(self, text: str):
#         """Parse the output of an LLM call."""
#         return text.strip().split(", ")


# template = """You are a helpful assistant who generates comma separated lists.
# A user will pass in a category, and you should generate 5 objects in that category in a comma separated list.
# ONLY return a comma separated list, and nothing more."""
# human_template = "{text}"

# chat_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", template),
#         ("human", human_template),
#     ]
# )
# chain = chat_prompt | llm | CommaSeparatedListOutputParser()
# result = chain.invoke({"text": "colors"})
# print(result)

############################## OutputParser ##############################


############################## RunnablePassthrough ##############################

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            # "作为中国保险经纪人，给客户介绍产品。",
            "你是一个以制造业为主的城市的市长",
            # "作为一个心理医生，请回答咨询的问题，格式如下：问题：\n......回答：\n1:......\n2:......\n",
        ),
        ("human", "{question}"),
    ]
)

llm.temperature = 0


runnable = (
    {"question": RunnablePassthrough()}
    | chat_prompt
    | llm
    | StrOutputParser()
)
# print(runnable.invoke("x raised to the third plus seven equals 12"))


runnable = chat_prompt | llm | StrOutputParser()
print(
    runnable.invoke(
        # {"question": "小学生有哪些前在的心理疾病？"}
        # {"question": "精神分裂症的原因有哪些？"}
        {"question": "制造业是国家经济命脉所系，是立国之本、强国之基。请结合全部给定材料，联系实际，围绕“把广东制造业这份厚实家当做优做强”这一主题，自拟题目，撰写一篇策论文。（50分）\n要求：\n（1）对策合理，紧密联系材料；\n（2）条理清晰，论证严密，合乎逻辑；\n（3）结构完整，表达准确，行文流畅；\n（4）篇幅在800-1000字。"}
    )
)

############################## RunnablePassthrough ##############################


############################## bind ##############################
# functions = [
#     {
#         "name": "solver",
#         "description": "Formulates and solves an equation",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "equation": {
#                     "type": "string",
#                     "description": "The algebraic expression of the equation",
#                 },
#                 "solution": {
#                     "type": "string",
#                     "description": "The solution to the equation",
#                 },
#             },
#             "required": ["equation", "solution"],
#         },
#     }
# ]

# llm.bind(function_call={"name": "solver"}, functions=functions)
# chat_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Write out the following equation using algebraic symbols then solve it. Use the format\n\nEQUATION:...\Step n:...\n\n",
#         ),
#         ("human", "{equation_statement}"),
#     ]
# )

# runnable = (
#     {"equation_statement": RunnablePassthrough()}
#     | chat_prompt
#     | llm
#     | StrOutputParser()
# )

# print(runnable.invoke("x raised to the third plus seven equals 12"))

############################## end ##############################


############################## Run arbitrary functions ##############################


# def length_function(text):
#     return len(text)


# def _multiple_length_function(text1, text2):
#     return len(text1) * len(text2)


# def multiple_length_function(_dict):
#     return _multiple_length_function(_dict["text1"], _dict["text2"])


# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Use the format: Step n:...\n",
#         ),
#         ("human", "what {a} and {b} represent and the result {a} * {b}"),
#     ]
# )
# # prompt = ChatPromptTemplate.from_template("what is {a} + {b}")

# # chain1 = prompt | llm
# # print()


# chain = (
#     {
#         "a": itemgetter("foo") | RunnableLambda(length_function),
#         "b": {"text1": itemgetter("foo"), "text2": itemgetter("bar")}
#         | RunnableLambda(multiple_length_function),
#     }
#     # | {"equation_statement": RunnablePassthrough()}
#     | prompt
#     | llm
# )

# print(chain.invoke({"foo": "fooabc", "bar": "baab"}))

############################## end ##############################
