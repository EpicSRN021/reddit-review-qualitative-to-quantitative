#TODO 
# ["comment", [metrics array], [weight factors array]]
# ["comment", score, [metrics array], weight]
# ["comments"](ordered), final score, final metrics
import math
import asyncio
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

async def summary(processed) -> str:
    prompt = f"""
    Given is a list of 5 Reddit comments reviewing a product, ,
    give a quick summary for a potential buyer.
    Reviews: {processed}
    """
    
    response = await client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}], max_completion_tokens=5000)
    return response.choices[0].message.content

async def compute_score(metrics):
    valid_metrics = [m for m in metrics if m != -1]
    return sum(valid_metrics) / len(valid_metrics) if valid_metrics else 0.0

async def compute_weight(weight_factors, credibility):
    if not weight_factors or len(weight_factors) != 4:
        return 1.0

    upvotes, karma, karma2, time_ago = weight_factors
    upvote_w = math.log(upvotes+1) /10
    karma_w = math.log((karma or 0)+1) /10
    karma2_w = math.log((karma2 or 0)+1) /10
    time_w = 1 / (1 + math.exp(0.08 * (time_ago - 60)))

    credibility_w = (credibility / 5) ** 2

    return 0.32 * upvote_w + 0.08  * karma_w + 0.24 * karma2_w + 0.2 * time_w + 0.24 * credibility_w

async def process_comments(comments):
    processed_full = []
    comments_with_weight = []
    
    total_weight = 0.0
    weighted_score_sum = 0.0
    weighted_metrics_sum = [0.0, 0.0, 0.0, 0.0]
    total_weight_per_metric = [0.0, 0.0, 0.0, 0.0] 

    for c in comments:
        text, url, metrics, weight_factors = c

        if not metrics or metrics[-1] == -1:
            continue

        score = await compute_score(metrics)
        weight = await compute_weight(weight_factors, metrics[-1])

        processed_full.append([text, url, score, metrics, weight])
        comments_with_weight.append(((text, url), weight))

        total_weight += weight
        weighted_score_sum += score * weight

        for i in range(4):
            if metrics[i] >= 0: 
                weighted_metrics_sum[i] += metrics[i] * weight
                total_weight_per_metric[i] += weight

    comments_with_weight.sort(key=lambda x: x[1], reverse=True)
    processed = [text for (text, _), _ in comments_with_weight]

    if total_weight == 0:
        final_score = 0.0
    else:
        final_score = weighted_score_sum / total_weight

    final_metrics = []
    for i in range(4):
        if total_weight_per_metric[i] > 0:
            final_metrics.append(weighted_metrics_sum[i] / total_weight_per_metric[i])
        else:
            final_metrics.append(0.0)

    top5 = [text for text, _ in processed[:5]]
    summ = await summary(top5)

    return processed, final_score, final_metrics, summ


