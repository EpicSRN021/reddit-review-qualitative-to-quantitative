import asyncio
import subprocess
import json
from reddit_api_call import get_reddit_tuples
from Classification import analyze_comment
from calculate import *
from data import *
import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
load_dotenv()
ENDPOINT = "https://unwrap-hackathon-oct-20-resource.cognitiveservices.azure.com/"
API_KEY = os.getenv("subscription_key")
MODEL = "gpt-5-mini"
client = AsyncAzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version="2024-12-01-preview"
)

commentlist = []
newdata = []

async def fetch_data(keyword):   
    # get reddit data: ("comment", "url", [weight factors])
    # send classification ["comment"] and get ("comment", [metrics])
    reddit_data = get_reddit_tuples(keyword, limit = 1)
    for data in reddit_data:
        commentlist.append(data[0])
        print(data[0])
    metrics =  await analyze_comment(commentlist)
    # metrics = json.loads(metricstring)
    print(metrics)
    for comment, url, weights in reddit_data: 
        if comment in metrics:
            metric = metrics[comment]
            newdata.append((comment, url, metric, weights))
    print(newdata)
            
    p, fs, fm, summ = await process_comments(newdata)

    return p, fs, fm, summ

        
async def fetch_pros_cons():
    prompt = f"""
    Given a list of Reddit reviews of a product, extract the main pros and cons based on the comments.
    For each pro or con, provide the text and the index of the review from the list it was based on.

    Your response should be in JSON format:
    {{
        "pros": [
            {{"text": "description of pro", "comment_index": 0}},
            {{"text": "another pro", "comment_index": 2}}
        ],
        "cons": [
            {{"text": "description of con", "comment_index": 1}},
            {{"text": "another con", "comment_index": 3}}
        ]
    }}

    Reviews: {commentlist}
    """
    
    response = await client.chat.completions.create(
        model=MODEL, 
        messages=[{"role": "user", "content": prompt}], 
        max_completion_tokens=5000,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    pros = []
    cons = []

    for item in result.get("pros", []):
        idx = item.get("comment_index")
        url = newdata[idx][1] if 0 <= idx < len(newdata) else None
        pros.append((item["text"], url))

    for item in result.get("cons", []):
        idx = item.get("comment_index")
        url = newdata[idx][1] if 0 <= idx < len(newdata) else None
        cons.append((item["text"], url))

    return pros, cons



  
