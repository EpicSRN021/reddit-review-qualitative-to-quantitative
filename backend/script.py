import asyncio
import subprocess
import json
import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from reddit_api_call import get_reddit_tuples
from Classification import analyze_comment
from calculate import *
from data import *
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


commentlist = []
newdata = []

# Load environment variables
load_dotenv()

# OpenAI client setup (same as in other files)
ENDPOINT = "https://unwrap-hackathon-oct-20-resource.cognitiveservices.azure.com/"
API_KEY = os.getenv("subscription_key")
MODEL = "gpt-5-mini"
client = AsyncAzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version="2024-12-01-preview"
)

async def generate_gpt_summary(product_name: str) -> str:
    """Generate a product summary using GPT when no Reddit comments are found"""
    try:
        prompt = f"""First, determine if "{product_name}" is a product that can be reviewed. If it's a product, create a review with 3 pros and 3 cons. If it's not a product (like a person, place, concept, etc.), respond with "NOT_A_PRODUCT".

If it's a product, use this exact format:

PROS:
1. [first advantage]
2. [second advantage] 
3. [third advantage]

CONS:
1. [first disadvantage]
2. [second disadvantage]
3. [third disadvantage]

Make each point specific and brief."""
        
        response = await client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "user", "content": prompt}], 
            max_completion_tokens=1000,
            reasoning_effort="low"
        )
        
        # Extract content - handle both standard and reasoning model responses
        summary = response.choices[0].message.content
        print(f"DEBUG: GPT response content: '{summary}'")
        
        # Check if GPT determined it's not a product
        if summary and "NOT_A_PRODUCT" in summary.upper():
            print(f"GPT determined '{product_name}' is not a product")
            return f"'{product_name}' is not a product that can be reviewed. Please search for an actual product instead."
        
        # If content is None or empty, try a simpler approach
        if not summary or len(summary.strip()) == 0:
            print(f"WARNING: GPT returned empty content. Trying alternative approach...")
            
            # Try a much simpler prompt
            simple_prompt = f"Is {product_name} a product? If yes, list 3 pros and 3 cons. If no, say 'NOT_A_PRODUCT'."
            simple_response = await client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": simple_prompt}],
                max_completion_tokens=1000,
                reasoning_effort="low"
            )
            summary = simple_response.choices[0].message.content
            
            # Check if fallback also determined it's not a product
            if summary and "NOT_A_PRODUCT" in summary.upper():
                print(f"Fallback GPT determined '{product_name}' is not a product")
                return f"'{product_name}' is not a product that can be reviewed. Please search for an actual product instead."
            
            # If still empty, provide a basic product summary
            if not summary or len(summary.strip()) == 0:
                print(f"WARNING: Even simple prompt returned empty content.")
                summary = f"The {product_name} is a product that may not have extensive Reddit discussion. For detailed reviews, consider checking manufacturer websites, Amazon reviews, or other review platforms. This product might be better known by alternative names or in specific communities."
        
        print(f"GPT Summary generated successfully ({len(summary)} characters)")
        return summary
        
    except Exception as e:
        print(f"ERROR in generate_gpt_summary: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Unable to generate summary due to an error: {str(e)}"

async def fetch_data(keyword):   
    # get reddit data: ("comment", "url", [weight factors])
    # send classification ["comment"] and get ("comment", [metrics])
    reddit_data = get_reddit_tuples(keyword, limit = 1)
    
    # Check if no comments were found
    if not reddit_data or len(reddit_data) == 0:
        print(f"No Reddit comments found for '{keyword}'. Generating GPT summary...")
        
        # Generate GPT summary for the product
        gpt_summary = await generate_gpt_summary(keyword)
        
        # Return empty data with GPT summary
        return [], [], [], gpt_summary
    
    commentlist = []
    for data in reddit_data:
        commentlist.append(data[0])
    metrics =  await analyze_comment(commentlist)
    # metrics = json.loads(metricstring)
    index = 1
    newdata = []
    for comment, url, weights in reddit_data: 
        if(index <= len(metrics)):
            metric = metrics[index]
        newdata.append((comment, url, metric, weights))
        index+=1
    
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
    
    # Parse the JSON response
    result = json.loads(response.choices[0].message.content)
    
    # Extract pros and cons with their comment indices
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
            


    # combine to get ("comment", "url", metrics, [weight factors])
    # call calculation.py with ^
