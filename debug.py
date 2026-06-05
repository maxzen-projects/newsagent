from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Return only this JSON array, no other text: [{\"title\": \"test\", \"summary\": \"hello\"}]"
        }
    ],
    temperature=0.2
)

print(repr(response.choices[0].message.content))