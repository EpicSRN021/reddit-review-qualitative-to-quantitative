import asyncio
import subprocess
import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from reddit_api_call import get_reddit_tuples
from Classification import analyze_comment
from calculate import *
from data import *
from cache import *
import hashlib
import re
cache = load_cache()
load_dotenv()
API_KEY = os.getenv("subscription_key")
MODEL = "gpt-5-mini"
REASONING = "low"
client = AsyncOpenAI(
    api_key=API_KEY
)


commentlist = []
newdata = []


async def generate_gpt_summary(product_name: str) -> str:
    cache_key = product_name + "sum"
    if cache_key in cache:
        print("Cache hit")
        return cache[cache_key]
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
        
        response = await client.responses.create(
            model=MODEL,
            input=prompt,
            max_output_tokens=500
        )
        
        
        # Extract content - handle both standard and reasoning model responses
        summary = response.output_text
        print(f"DEBUG: GPT response content: '{summary}'")
        
        # Check if GPT determined it's not a product
        if summary and "NOT_A_PRODUCT" in summary.upper():
            print(f"GPT determined '{product_name}' is not a product")
            response = f"'{product_name}' is not a product that can be reviewed. Please search for an actual product instead."
            cache[cache_key] = response
            save_cache(cache)
            return response
        
        # If content is None or empty, try a simpler approach
        if not summary or len(summary.strip()) == 0:
            print(f"WARNING: GPT returned empty content. Trying alternative approach...")
            
            # Try a much simpler prompt
            simple_prompt = f"Is {product_name} a product? If yes, list 3 pros and 3 cons. If no, say 'NOT_A_PRODUCT'."
            simple_response = await client.responses.create(
                model=MODEL,
                input=simple_prompt,
                max_output_tokens=500
            )
            summary = simple_response.output_text
        
            
            
            # Check if fallback also determined it's not a product
            if summary and "NOT_A_PRODUCT" in summary.upper():
                print(f"Fallback GPT determined '{product_name}' is not a product")
                summary = f"'{product_name}' is not a product that can be reviewed. Please search for an actual product instead."
                cache[cache_key] = summary
                save_cache(cache)
                return summary
            # If still empty, provide a basic product summary
            if not summary or len(summary.strip()) == 0:
                print(f"WARNING: Even simple prompt returned empty content.")
                summary = f"The {product_name} is a product that may not have extensive Reddit discussion. For detailed reviews, consider checking manufacturer websites, Amazon reviews, or other review platforms. This product might be better known by alternative names or in specific communities."
                cache[cache_key] = summary
                save_cache(cache)
                return summary
        
        print(f"GPT Summary generated successfully ({len(summary)} characters)")
        cache[cache_key] = summary
        save_cache(cache)
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
        
        # Check if GPT determined it's not a product
        if gpt_summary and "not a product" in gpt_summary.lower():
            print(f"GPT determined '{keyword}' is not a product")
            return [], [], [], gpt_summary, [], [], True  # Add is_not_product flag
        
        # Return empty data with GPT summary
        return [], [], [], gpt_summary, [], [], False
    
    commentlist = []
    for data in reddit_data:
        commentlist.append(data[0])
    metrics =  await analyze_comment(commentlist)
    # metrics = json.loads(metricstring)
    index = 0
    newdata = []
    for comment, url, weights in reddit_data: 
        if(index <= len(metrics)):
            metric = metrics[index]
        newdata.append((comment, url, metric, weights))
        index+=1
    
    p, fs, fm, summ = await process_comments(newdata)
    
    # Extract pros and cons from Reddit comments
    print(f"🔍 Extracting pros and cons from Reddit comments...")
    print(f"DEBUG: commentlist length: {len(commentlist)}")
    print(f"DEBUG: newdata length: {len(newdata)}")
    try:
        pros, cons = await fetch_pros_cons(commentlist, newdata)
        print(f"✓ Found {len(pros)} pros and {len(cons)} cons from Reddit comments")
    except Exception as e:
        print(f"⚠️ Failed to extract pros/cons from Reddit comments: {e}")
        import traceback
        traceback.print_exc()
        pros, cons = [], []

    return p, fs, fm, summ, pros, cons, False  # is_not_product = False for normal products

async def fetch_pros_cons(commentlist, newdata):
    normalized = sorted(commentlist)
    joined = "\n".join(normalized)
    hash_value = hashlib.sha256(joined.encode()).hexdigest()
    cache_key = hash_value
    if cache_key in cache:
        print("Cache hit")
        pros, cons = cache[cache_key]
        return pros, cons
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
    
    response = await client.responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=5000
    )
    # Parse the JSON response
    result = json.loads(response.output_text)
    
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
    cache[cache_key] = [pros, cons]
    save_cache(cache)
    return pros, cons        
            


    # combine to get ("comment", "url", metrics, [weight factors])
    # call calculation.py with ^
