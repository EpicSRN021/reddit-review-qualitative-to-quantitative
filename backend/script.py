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

async def fetch_data(keyword):   
    # get reddit data: ("comment", "url", [weight factors])
    # send classification ["comment"] and get ("comment", [metrics])
    reddit_data = get_reddit_tuples(keyword, limit = 1)
   
    commentlist = []
    for data in reddit_data:
        commentlist.append(data[0])
    metrics =  await analyze_comment(commentlist)
    # metrics = json.loads(metricstring)
    newdata = []
    for comment, url, weights in reddit_data: 
        if comment in metrics:
            metric = metrics[comment]
            newdata.append((comment, url, metric, weights))
            
    p, fs, fm, summ = await process_comments(newdata)

    return p, fs, fm, summ

        
async def fetch_pros_cons():
    prompt = f"""
    Given a list of Reddit reviews of a product, give me a list the main pros and cons based on the comments.
    If it is pro label with 1, and con label with 0. 
    For each pro or con give me the index of the review from the list provided.

    Your response should be in the following format:
    {"blah blah", 0, 32}
    {"blah blah", 1, 3}
    {"blah blah", 1, 2}...
    

    Reviews: {commentlist}
    """
    
    response = await client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], max_completion_tokens=5000)
    return response.choices[0].message.content



  
