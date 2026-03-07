import asyncio
from openai import AsyncOpenAI

async def test():
    client = AsyncOpenAI(
        api_key="cs-sk-7161ac23-ef5b-4180-ae88-0e4eef0b0004",
        base_url="http://127.0.0.1:23333/v1",
    )
    print("Sending request...")
    try:
        stream = await client.chat.completions.create(
            model="zhipu:glm-5",
            messages=[{"role": "user", "content": "hello, write a 20 word story"}],
            stream=True
        )
        print("Got stream object, iterating...")
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            # Some APIs structure chunks differently when reasoning is involved
            print("CHUNK:", delta)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
