#!/usr/bin/env python3
"""
High-level wrapper to:
  1) Search Reddit for a product keyword using backend/data.py
  2) Fetch full posts + comments
  3) Refactor to tuples using backend/data_refactor.py

Primary entrypoint:
    get_reddit_tuples(product_name: str, *, subreddit="all", time_filter="year", limit=100, comments=30,
                      query: str | None = None) -> list[tuple]

Returns a list of tuples shaped like:
    (
      comment_text: str,
      comment_url: str,
      [post_score: int, user_total_karma: int | None, comment_score: int, post_age_months: float]
    )

CLI usage:
    python reddit_api_call.py "MacBook Air" --subreddit 'apple+macbook+macbookair+macbookpro' --limit 100 --comments 30

To use Google Custom Search instead of Reddit search:
    python backend/reddit_api_call.py "MacBook Air" --source google --limit 10 --comments 30
Requires GOOGLE_API_KEY and GOOGLE_CSE_ID in your environment.

Requires env vars for PRAW:
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

# Ensure repo root on sys.path when running as a script
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    # When executed as a package module: python -m backend.reddit_api_call
    from .data import search_and_fetch  # type: ignore
    from .data_refactor import build_comment_tuples_from_jsonl  # type: ignore
    from .data import fetch_post_data  # type: ignore
    from .google_search import get_top_reddit_reviews  # type: ignore
except Exception:
    # When executed as a script: python backend/reddit_api_call.py
    from backend.data import search_and_fetch  # type: ignore
    from backend.data_refactor import build_comment_tuples_from_jsonl  # type: ignore
    from backend.data import fetch_post_data  # type: ignore
    from backend.google_search import get_top_reddit_reviews  # type: ignore


TmpMeta = "_tmp_search_meta.json"
TmpJsonl = "_tmp_search_results.jsonl"


def _write_jsonl(records: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _fetch_via_google(product_name: str, limit: int, comments: int) -> None:
    # Use Google Custom Search to find top Reddit URLs and fetch them one by one.
    urls = get_top_reddit_reviews(product_name, num_results=limit)
    results: list[dict] = []
    for i, url in enumerate(urls, start=1):
        try:
            data_obj = fetch_post_data(url, max_comments=comments)
            if data_obj:
                results.append(data_obj)
        except Exception as e:
            # Skip bad URLs but continue
            print(f"[google-fetch] Skipping URL {i}/{len(urls)}: {url} ({e})")
            continue
    # Write JSONL so data_refactor can consume it directly
    _write_jsonl(results, TmpJsonl)
    # Also write a tiny meta file for parity with search_and_fetch
    meta = {"source": "google", "keyword": product_name, "count": len(results), "urls": urls}
    with open(TmpMeta, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _default_query_for_product(product_name: str) -> str:
    # Prefer titles that include the product and the word review; exclude NSFW
    # Example: title:MacBook AND title:review nsfw:no
    # If the product has spaces, wrap in quotes for title field
    pname = product_name.strip()
    if " " in pname:
        pname_token = f'"{pname}"'
    else:
        pname_token = pname
    return f"title:{pname_token} AND title:review nsfw:no"


def get_reddit_tuples(
    product_name: str,
    *,
    subreddit: Optional[str] = "all",
    time_filter: str = "year",
    sort: str = "relevance",
    limit: int = 100,
    comments: int = 30,
    include_commenter_karma: bool = False,
    max_commenter_profiles: int = 200,
    query: Optional[str] = None,
    source: str = "reddit",
) -> List[Tuple[str, str, list[Any]]]:
    """
    Orchestrate search -> fetch -> refactor and return comment tuples.
    """
    q = query or _default_query_for_product(product_name)

    if source == "google":
        # Fetch via Google → URLs → JSONL
        _fetch_via_google(product_name, limit=limit, comments=comments)
    else:
        # Default: Reddit API search → JSONL
        search_and_fetch(
            query=q,
            subreddit=subreddit,
            sort=sort,
            time_filter=time_filter,
            limit=limit,
            max_comments=comments,
            include_commenter_karma=include_commenter_karma,
            max_commenter_profiles=max_commenter_profiles,
            posts_json_path=TmpMeta,
            posts_jsonl_path=TmpJsonl,
        )

    tuples = build_comment_tuples_from_jsonl(TmpJsonl)
    return tuples


def main() -> None:
    ap = argparse.ArgumentParser(description="Get Reddit tuples for a product name (search -> fetch -> refactor).")
    ap.add_argument("product", help="Product name, e.g., 'MacBook Air' or 'iPhone 16 Pro'")
    ap.add_argument("--subreddit", default="all", help="Subreddit or multi (e.g., 'apple+macbook')")
    ap.add_argument("--time-filter", default="year", choices=["all","day","hour","month","week","year"], help="Search window")
    ap.add_argument("--sort", default="relevance", choices=["relevance","hot","top","new","comments"], help="Search sort")
    ap.add_argument("--limit", type=int, default=100, help="Max posts to fetch (API cap ~1000)")
    ap.add_argument("--comments", type=int, default=30, help="Max comments per post")
    ap.add_argument("--source", default="reddit", choices=["reddit", "google"], help="Where to get candidate posts from")
    ap.add_argument("--commenter-karma", action="store_true", help="Try to fetch commenter karma (slower)")
    ap.add_argument("--max-commenter-profiles", type=int, default=200, help="Max distinct profiles to look up for karma")
    ap.add_argument("--query", default=None, help="Override auto query (advanced)")
    args = ap.parse_args()

    tuples = get_reddit_tuples(
        args.product,
        subreddit=args.subreddit,
        time_filter=args.time_filter,
        sort=args.sort,
        limit=args.limit,
        comments=args.comments,
        include_commenter_karma=args.commenter_karma,
        max_commenter_profiles=args.max_commenter_profiles,
        query=args.query,
        source=args.source,
    )

    # Print as JSON for quick consumption
    print(json.dumps(tuples, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()