import os
from openai import OpenAI
import base64
import time

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("请先设置 OPENAI_API_KEY 环境变量，或在代码中直接填写 api_key！")


#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image_1 = encode_image("/home/bughero/Desktop/car_4s_store.jpg")
base64_image_2 = encode_image("/home/bughero/Desktop/1080p.jpg")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

start = time.time()
completion = client.chat.completions.create(
    # model="qwen-vl-max-latest",  # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
    model="qwen-vl-plus-latest",  # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image_1}"},
                    # "image_url": {
                    #     "url": "https://static.tuputech.com/api/image/original/bi-api/storage-weed201/2025-06-27/00-14/43FECAHPBVD89EA/1750954682166.4501644057607897.jpg"
                    # },
                },
                {
                    "type": "text",
                    "text": "图片中有没有出现【顾客手持手机、手机支付二维码、现金】。如果有，请用 json {'customer_holding_mobile_phone': bool, 'mobile_payment_QR_code':bool, 'cash': bool} 格式返回，只需要返回json结果即可，不需要分析过程、解释、说明。",
                },
            ],
        },
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "image_url",
        #             # "image_url": {"url": f"data:image/jpeg;base64,{base64_image_2}"},
        #             "image_url": {
        #                 "url": "https://static.tuputech.com/api/image/original/bi-api/storage-weed201/2025-06-26/19-35/6569b094dc6c4299ddb06da6/17509374981440.35695866275741195.jpg"
        #             },
        #         },
        #         {
        #             "type": "text",
        #             "text": "图片中有没有出现【顾客手持手机、手机支付二维码、现金】。如果有，请用 json 格式返回上述选项。",
        #         },
        #     ],
        # },
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "image_url",
        #             # "image_url": {"url": f"data:image/jpeg;base64,{base64_image_2}"},
        #             "image_url": {
        #                 "url": "https://static.tuputech.com/api/image/original/bi-api/storage-weed233/2025-06-26/17-14/637FCACPBV72979/1750929739508.5636369517505253.jpg"
        #             },
        #         },
        #         {
        #             "type": "text",
        #             "text": "图片中有没有出现【顾客手持手机、手机支付二维码、现金】。如果有，请用 json 格式返回上述选项。",
        #         },
        #     ],
        # },
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "image_url",
        #             # "image_url": {"url": f"data:image/jpeg;base64,{base64_image_2}"},
        #             "image_url": {
        #                 "url": "https://static.tuputech.com/api/image/original/bi-api/storage-sw52/2025-06-27/02-14/43FECAHPBV45820/1750962196953.3580927135438090.jpg"
        #             },
        #         },
        #         {
        #             "type": "text",
        #             "text": "图片中有没有出现【顾客手持手机、手机支付二维码、现金】。如果有，请用 json 格式返回上述选项。",
        #         },
        #     ],
        # },
    ],
)
end = time.time()

print(completion.choices[0].message.content)
print(f"LLM api 耗时: {int((end - start)*1000)} ms")
print(f"模型: {completion.model}")
if hasattr(completion, "usage") and completion.usage:
    print(f"prompt_tokens: {completion.usage.prompt_tokens}")
    print(f"completion_tokens: {completion.usage.completion_tokens}")
    print(f"total_tokens: {completion.usage.total_tokens}")
