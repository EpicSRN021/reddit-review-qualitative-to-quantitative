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

def search_and_fetch(
    query: str,
    subreddit: Optional[str] = None,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 20,
    max_comments: int = 100,
    include_commenter_karma: bool = False,
    max_commenter_profiles: int = 200,
    posts_json_path: str = "search_results.json",
    posts_jsonl_path: str = "search_posts.jsonl",
) -> None:
    """
    Search Reddit for submissions matching the query and fetch full post/comment data for each.
    Saves the search results metadata to a JSON file, and full post+comments to a JSONL file.
    Prints progress to stdout.
    """
    reddit = get_reddit_client()
    subreddit_obj = reddit.subreddit(subreddit) if subreddit else reddit.subreddit("all")
    print(f"Searching for '{query}' in subreddit='{subreddit or 'all'}' (sort={sort}, time_filter={time_filter}, limit={limit})")
    submissions = []
    for i, subm in enumerate(subreddit_obj.search(query, sort=sort, time_filter=time_filter, limit=limit)):
        post_meta = {
            "id": subm.id,
            "title": subm.title,
            "subreddit": str(subm.subreddit),
            "author": str(subm.author) if subm.author else None,
            "created_utc": float(subm.created_utc),
            "permalink": f"https://www.reddit.com{subm.permalink}",
            "url": subm.url,
            "score": int(subm.score),
            "num_comments": int(subm.num_comments),
        }
        submissions.append(post_meta)
    print(f"Found {len(submissions)} submissions. Writing metadata to {posts_json_path}")
    with open(posts_json_path, "w", encoding="utf-8") as f:
        json.dump(submissions, f, indent=2, ensure_ascii=False)

    print(f"Fetching full post and comments for each submission; writing to {posts_jsonl_path}")
    with open(posts_jsonl_path, "w", encoding="utf-8") as fout:
        for idx, meta in enumerate(submissions, 1):
            print(f" [{idx}/{len(submissions)}] Fetching post {meta['id']} ...")
            try:
                post_data = fetch_post_data(
                    meta["permalink"],
                    max_comments=max_comments,
                    include_commenter_karma=include_commenter_karma,
                    max_commenter_profiles=max_commenter_profiles,
                )
                fout.write(json.dumps(post_data, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"   Error fetching post {meta['id']}: {e}")
    print("Done.")


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


def fetch_post_data(
    url_or_id: str,
    max_comments: int = 100,
    include_commenter_karma: bool = False,
    max_commenter_profiles: int = 200,
    reddit: Optional[praw.Reddit] = None,
) -> Dict[str, Any]:
    """
    Fetch submission metrics and up to `max_comments` flattened comments.
    """
    subm = get_submission(url_or_id, reddit=reddit)

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
                    "comment_url": f"https://www.reddit.com{subm.permalink}{c.id}",
                }
            )
    except Exception as e:
        # If comments fail, still return post data
        comments = [{"error": f"Failed to fetch/flatten comments: {e}"}]

    return {"post": post, "comments": comments}


def fetch_from_urls(urls, max_comments=20, out_json="posts_from_urls.json"):
    reddit = get_reddit_client()
    results = []
    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] Fetching {url}")
        data = fetch_post_data(url, max_comments=max_comments, reddit=reddit)
        results.append(data)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Done. Wrote {len(results)} posts to {out_json}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch Reddit post data or search and fetch multiple posts.")
    parser.add_argument("url_or_id_or_query", nargs="?", help="Reddit post URL/base36 ID (default), or search query if --search is set")
    parser.add_argument(
        "--comments", type=int, default=50, help="Max number of comments to return/fetch per post (default: 50)"
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output (for single post mode)"
    )
    parser.add_argument("--commenter-karma", action="store_true", help="If set, fetch karma for distinct comment authors (rate-limited; cached).")
    parser.add_argument("--max-commenter-profiles", type=int, default=200, help="Max distinct commenter profiles to look up for karma (default: 200).")
    parser.add_argument("--search", action="store_true", help="If set, treat positional arg as a search query and fetch multiple posts.")
    parser.add_argument("--subreddit", type=str, default=None, help="Subreddit to search (default: all)")
    parser.add_argument("--sort", type=str, default="relevance", help="Sort for search (relevance, hot, top, new, comments)")
    parser.add_argument("--time-filter", type=str, default="all", help="Time filter for search (all, day, hour, month, week, year)")
    parser.add_argument("--limit", type=int, default=20, help="Max number of search results to fetch (default: 20)")
    parser.add_argument("--posts-json-path", type=str, default="search_results.json", help="Path to save search results metadata (default: search_results.json)")
    parser.add_argument("--posts-jsonl-path", type=str, default="search_posts.jsonl", help="Path to save full post+comments JSONL (default: search_posts.jsonl)")
    parser.add_argument("--urls-file", type=str, default=None, help="Path to a text file with one Reddit post URL per line; skips search and fetches those posts directly")
    parser.add_argument("--out-json", type=str, default="posts_from_urls.json", help="Output JSON path when using --urls-file (default: posts_from_urls.json)")
    args = parser.parse_args()

    if args.urls_file:
        urls = [u.strip() for u in open(args.urls_file, "r", encoding="utf-8") if u.strip()]
        fetch_from_urls(urls, max_comments=args.comments, out_json=args.out_json)
        return

    if args.search:
        search_and_fetch(
            query=args.url_or_id_or_query,
            subreddit=args.subreddit,
            sort=args.sort,
            time_filter=args.time_filter,
            limit=args.limit,
            max_comments=args.comments,
            include_commenter_karma=args.commenter_karma,
            max_commenter_profiles=args.max_commenter_profiles,
            posts_json_path=args.posts_json_path,
            posts_jsonl_path=args.posts_jsonl_path,
        )
    else:
        data = fetch_post_data(
            args.url_or_id_or_query,
            max_comments=args.comments,
            include_commenter_karma=args.commenter_karma,
            max_commenter_profiles=args.max_commenter_profiles,
        )
        if args.pretty:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(data, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()