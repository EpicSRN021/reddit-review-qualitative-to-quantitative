import asyncio
import os
import re
import json
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
load_dotenv()
ENDPOINT = "https://unwrap-hackathon-oct-20-resource.cognitiveservices.azure.com/"
API_KEY = os.getenv("subscription_key")
MODEL = "gpt-5-mini"
REASONING = "low"
client = AsyncAzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version="2024-12-01-preview"
)
async def analyze_comment(reviews: list[str]) -> dict[str, list[int]]:
    print(reviews)
    prompt = f"""
    Given is a list of Reddit comments reviewing a product, 
    analyze each review and rate it from 0-5 for:
    - quality
    - cost
    - availability
    - utility
    - credibility

    If the review doesn't relate to a metric, rate it -1. If it's not related to any of the metrics rate its credibility -1. 

    Return ONLY a VALID JSON in this format where the reviews are the keys and the values are lists of integers of the metrics. Do not reason or question. 
    {{
        "original review comment": [quality, cost, availability, utility, credibility],
        "second review": [quality, cost, availability, utility, credibility],
        ...
    }}

    Reviews: {reviews}
    """
    
    response = await client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], max_completion_tokens=10000, reasoning_effort= REASONING)
    r = response.choices[0].message.content

    print(r)
    r = r.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')

# Escape unescaped backslashes
    r = re.sub(r'(?<!\\)\\(?![\\/"bfnrtu])', r'\\\\', r)

# Optionally remove trailing commas before closing braces/brackets
    r = re.sub(r',(\s*[}\]])', r'\1', r)


    try:
        r = json.loads(r)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print(r)
        r = {}
    
    return r



    
    
