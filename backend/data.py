"""
Reddit data fetching utilities.

Features:
- Initialize a read-only Reddit client (via PRAW) using environment variables.
- Fetch a submission by URL or by base36 ID.
- Return post metrics: score (post karma), upvote ratio, estimated upvotes/downvotes, and more.
- Fetch and return a flattened list of comments (up to a limit).
- Simple CLI for quick testing:
    python backend/data.py https://www.reddit.com/r/Python/comments/xxxxx/some_post/ --comments 50
Requirements:
- praw
- python-dotenv (optional, for loading a .env file)
Environment variables:
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT  (e.g., "unwrapathon:reddit-scraper:v1.0 (by u/yourusername)")
"""

from __future__ import annotations

import argparse
import json
import math
import os
from typing import Dict, Any, List, Tuple, Optional

try:
    # Optional: only used if python-dotenv is installed and a .env file exists
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

import praw  # type: ignore


def _env(name: str, default: Optional[str] = None) -> str:
    v = os.getenv(name, default)
    if v is None or v.strip() == "":
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it in your shell or a .env file."
        )
    return v


def get_reddit_client() -> praw.Reddit:
    """
    Initialize a read-only PRAW client using env vars.
    Required:
        REDDIT_CLIENT_ID
        REDDIT_CLIENT_SECRET
        REDDIT_USER_AGENT
    """
    client_id = _env("REDDIT_CLIENT_ID")
    client_secret = _env("REDDIT_CLIENT_SECRET")
    user_agent = _env("REDDIT_USER_AGENT")

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        check_for_async=False,
    )
    reddit.read_only = True
    return reddit


def get_submission(url_or_id: str, reddit: Optional[praw.Reddit] = None):
    """
    Retrieve a Submission either by full URL or by the base36 ID.
    """
    r = reddit or get_reddit_client()
    if url_or_id.startswith("http://") or url_or_id.startswith("https://"):
        return r.submission(url=url_or_id)
    return r.submission(id=url_or_id)


def estimate_votes(score: int, upvote_ratio: Optional[float]) -> Tuple[Optional[int], Optional[int]]:
    """
    Reddit does not expose raw upvote/downvote counts.
    You can estimate using:
        score = U - D
        ratio = U / (U + D)
    Solve:
        U = score * ratio / (2*ratio - 1)
        D = U * (1 - ratio) / ratio
    Edge cases:
        - ratio == 0.5 => denominator 0; if score ~= 0, counts are indeterminate.
        - ratio in {0, 1} => all votes one-sided.
    Returns (estimated_upvotes, estimated_downvotes), possibly None if indeterminate.
    """
    if upvote_ratio is None:
        return (None, None)

    r = upvote_ratio
    # Clamp for safety
    r = max(0.0, min(1.0, r))

    if r == 1.0:
        return (max(score, 0), 0)
    if r == 0.0:
        return (0, max(-score, 0))

    denom = (2 * r - 1.0)
    if abs(denom) < 1e-12:
        if score == 0:
            return (None, None)
        # If ratio ~ 0.5 but non-zero score, fall back to a best-effort split
        # where total votes T = |score| / epsilon; not meaningful, return None.
        return (None, None)

    # Compute and round to nearest int (cannot be negative)
    u_est = score * r / denom
    d_est = u_est * (1.0 - r) / r
    u_int = max(0, int(round(u_est)))
    d_int = max(0, int(round(d_est)))
    return (u_int, d_int)


def fetch_post_data(url_or_id: str, max_comments: int = 100, include_commenter_karma: bool = False, max_commenter_profiles: int = 200) -> Dict[str, Any]:
    """
    Fetch submission metrics and up to `max_comments` flattened comments.
    """
    subm = get_submission(url_or_id)

    commenter_cache: Dict[str, Tuple[Optional[int], Optional[int]]] = {}
    profiles_looked_up = 0

    subm.comment_sort = "top"  # or "new", etc.

    # Basic post metrics
    author_name = str(subm.author) if subm.author else None
    author_link_karma = None
    author_comment_karma = None
    try:
        if subm.author is not None:
            # Public author karma is usually available for read-only
            author_link_karma = getattr(subm.author, "link_karma", None)
            author_comment_karma = getattr(subm.author, "comment_karma", None)
    except Exception:
        pass

    up_est, down_est = estimate_votes(subm.score, getattr(subm, "upvote_ratio", None))

    post: Dict[str, Any] = {
        "id": subm.id,
        "title": subm.title,
        "subreddit": str(subm.subreddit),
        "author": author_name,
        "author_link_karma": author_link_karma,
        "author_comment_karma": author_comment_karma,
        "created_utc": float(subm.created_utc),
        "is_nsfw": bool(getattr(subm, "over_18", False)),
        "permalink": f"https://www.reddit.com{subm.permalink}",
        "url": subm.url,
        # Voting-related
        "score": int(subm.score),              # This is the post "karma"
        "upvote_ratio": float(getattr(subm, "upvote_ratio", math.nan)),
        "estimated_upvotes": up_est,
        "estimated_downvotes": down_est,
        # Comments metadata
        "num_comments": int(subm.num_comments),
    }

    # Fetch comments (flattened)
    comments: List[Dict[str, Any]] = []
    try:
        subm.comments.replace_more(limit=0)  # Avoid MoreComments objects
        flat = list(subm.comments.list())
        for c in flat[: max(0, max_comments)]:
            if not hasattr(c, "body"):
                continue
            author = str(c.author) if c.author else None

            author_link_karma_c = None
            author_comment_karma_c = None
            if include_commenter_karma and author:
                if author in commenter_cache:
                    author_link_karma_c, author_comment_karma_c = commenter_cache[author]
                elif profiles_looked_up < max_commenter_profiles:
                    try:
                        redditor = subm._reddit.redditor(author)
                        author_link_karma_c = getattr(redditor, "link_karma", None)
                        author_comment_karma_c = getattr(redditor, "comment_karma", None)
                    except Exception:
                        author_link_karma_c = None
                        author_comment_karma_c = None
                    commenter_cache[author] = (author_link_karma_c, author_comment_karma_c)
                    profiles_looked_up += 1

            comments.append(
                {
                    "id": c.id,
                    "author": author,
                    "body": c.body,
                    "score": int(getattr(c, "score", 0)),
                    "created_utc": float(getattr(c, "created_utc", 0.0)),
                    "parent_id": getattr(c, "parent_id", None),
                    "author_link_karma": author_link_karma_c,
                    "author_comment_karma": author_comment_karma_c,
                }
            )
    except Exception as e:
        # If comments fail, still return post data
        comments = [{"error": f"Failed to fetch/flatten comments: {e}"}]

    return {"post": post, "comments": comments}


def main():
    parser = argparse.ArgumentParser(description="Fetch Reddit post data.")
    parser.add_argument("url_or_id", help="Reddit post URL or base36 ID")
    parser.add_argument(
        "--comments", type=int, default=50, help="Max number of comments to return (default: 50)"
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    parser.add_argument("--commenter-karma", action="store_true", help="If set, fetch karma for distinct comment authors (rate-limited; cached).")
    parser.add_argument("--max-commenter-profiles", type=int, default=200, help="Max distinct commenter profiles to look up for karma (default: 200).")
    args = parser.parse_args()

    data = fetch_post_data(args.url_or_id, max_comments=args.comments, include_commenter_karma=args.commenter_karma, max_commenter_profiles=args.max_commenter_profiles)
    if args.pretty:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()