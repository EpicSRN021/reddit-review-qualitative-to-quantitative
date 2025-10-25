import asyncio
import subprocess
from reddit_api_call import get_reddit_tuples
from Classification import analyze_comment
from calculate import *
from data import *


async def fetch_data(keyword):   
    # get reddit data: ("comment", "url", [weight factors])
    # send classification ["comment"] and get ("comment", [metrics])
    reddit_data = get_reddit_tuples(keyword)
   
    commentlist = []
    for data in reddit_data:
        commentlist.append(data[0])
    metrics =  await analyze_comment(commentlist)
    newdata = []
    for comment, url, weights in reddit_data: 
        if comment in metrics:
            metric = metrics[comment]
            newdata.append((comment, url, metric, weights))
            
    return process_comments(newdata)


        
            


    # combine to get ("comment", "url", metrics, [weight factors])
    # call calculation.py with ^