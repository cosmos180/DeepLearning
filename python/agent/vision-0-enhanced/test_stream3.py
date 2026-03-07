import asyncio
from openai import AsyncOpenAI
import json

async def test():
    client = AsyncOpenAI(
        api_key="cs-sk-7161ac23-ef5b-4180-ae88-0e4eef0b0004",
        base_url="http://127.0.0.1:23333/v1",
    )
    print("Sending request...")
    try:
        stream = await client.chat.completions.create(
            model="zhipu:glm-5",
            messages=[{"role": "user", "content": "hi"}],
            stream=True
        )
        print("Got stream object, iterating...")
        async for chunk in stream:
            # Print the raw dict representation of the chunk
            data = chunk.model_dump()
            delta = data['choices'][0]['delta']
            content = delta.get('content')
            reasoning = delta.get('reasoning_content')
            print(f"C: '{content}' R: '{reasoning}'")
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
