import math


#TODO 
# ["comment", [metrics array], [weight factors array]]
# ["comment", score, [metrics array], weight]
# ["comments"](ordered), final score, final metrics


import math

def compute_score(metrics):
    return sum(metrics) / len(metrics) if metrics else 0.0

def compute_weight(weight_factors):
    if not weight_factors or len(weight_factors) != 4:
        return 1.0

    upvotes, karma, time_ago, credibility = weight_factors
    upvote_w = math.log(upvotes+1) /10
    karma_w = math.log(karma+1) /10
    time_w = math.exp(-0.05 * time_ago)
    credibility_w = (credibility / 5) ** 2

    return 0.32 * upvote_w + 0.32 * karma_w + 0.2 * time_w + 0.24 * credibility_w

def process_comments(comments):
    processed_full = []  # keep full info for calculation
    comments_with_weight = []  # for sorting comment texts
    total_weight = 0.0
    weighted_score_sum = 0.0
    weighted_metrics_sum = [0.0, 0.0, 0.0, 0.0]

    for c in comments:
        text, metrics, weight_factors = c
        score = compute_score(metrics)
        weight = compute_weight(weight_factors)

        processed_full.append([text, score, metrics, weight])
        comments_with_weight.append((text, weight))

        # accumulate for final score/metrics
        total_weight += weight
        weighted_score_sum += score * weight
        for i in range(4):
            weighted_metrics_sum[i] += metrics[i] * weight

    # sort comment texts by weight descending
    comments_with_weight.sort(key=lambda x: x[1], reverse=True)
    processed = [text for text, _ in comments_with_weight]

    if total_weight == 0:
        final_score = 0.0
        final_metrics = [0.0, 0.0, 0.0, 0.0]
    else:
        final_score = weighted_score_sum / total_weight
        final_metrics = [m / total_weight for m in weighted_metrics_sum]

    return processed, final_score, final_metrics



