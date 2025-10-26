import asyncio
import subprocess
import json
from reddit_api_call import get_reddit_tuples
from Classification import analyze_comment
from calculate import *
from data import *

async def fetch_data(keyword):   
    # get reddit data: ("comment", "url", [weight factors])
    # send classification ["comment"] and get ("comment", [metrics])
    reddit_data = get_reddit_tuples(keyword, limit = 3)
    
    commentlist = []
    for data in reddit_data:
        commentlist.append(data[0])
    metrics =  await analyze_comment(commentlist)
    # metrics = json.loads(metricstring)
    newdata = []
    index = 1
    for comment, url, weights in reddit_data: 
        if(index <= len(metrics)):
            metric = metrics[index]
        newdata.append((comment, url, metric, weights))
        index+=1
    
    p, fs, fm, summ = await process_comments(newdata)

    return p, fs, fm, summ


        
            


    # combine to get ("comment", "url", metrics, [weight factors])
    # call calculation.py with ^
