import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
    api_key=os.getenv("FEATHERLESS_API_KEY"),
)

response = client.chat.completions.create(
    model=os.getenv("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324"),
    messages=[
        {
            "role": "system",
            "content": "You are MenuTaste, an AI food product analysis agent.",
        },
        {
            "role": "user",
            "content": "Analyze an Ethiopian chickpea breakfast bowl for a cafe in Milan.",
        },
    ],
    temperature=0.3,
    max_tokens=500,
)

print(response.choices[0].message.content)