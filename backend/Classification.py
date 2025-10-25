import asyncio
import os
import ast
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
load_dotenv()
ENDPOINT = "https://unwrap-hackathon-oct-20-resource.cognitiveservices.azure.com/"
API_KEY = os.getenv("subscription_key")
MODEL = "gpt-5-nano"
REASONING = "low"
client = AsyncAzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version="2024-12-01-preview"
)
async def analyze_comment(reviews: list[str]) -> dict[str, list[int]]:
    prompt = f"""
    Given is a list of Reddit comments reviewing a product, 
    analyze each review and rate it from 0-5 for:
    - quality
    - cost
    - availability
    - utility
    - credibility

    If the review doesn't relate to a metric, rate it -1. If it's not related to any of the metrics rate its credibility -1. 

    Return a Python dictionary in this format where the reviews are the keys and the values are lists of integers of the metrics. 
    {{
        "original review comment": [quality, cost, availability, utility, credibility],
        "second review": [quality, cost, availability, utility, credibility],
        ...
    }}

    Reviews: {reviews}
    """
    
    response = await client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], max_completion_tokens=5000, reasoning_effort= REASONING)
    r = response.choices[0].message.content

     try:
        r = ast.literal_eval(raw_output)
    except Exception as e:
        print("Failed to parse output:", e)
        print(r)
        r = {}
    
    return r



    
    
