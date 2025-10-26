#!/usr/bin/env python3
"""
Refactor utilities built on top of backend/data.py.

Goal: given a dataset produced by backend/data.py (JSONL where each line is
{"post": {...}, "comments": [...]}), produce an array of tuples for every
comment across all posts.

Each tuple structure:
(
  actual_comment_string: str,
  comment_url_string: str,
  details: [
    post_score: int,
    user_total_karma: int | None,   # author_link_karma + author_comment_karma (if known)
    comment_score: int,
    post_age_ago: str               # e.g., "3d", "5h", "2y"
  ]
)

CLI:
  python backend/data_refactor.py --in-jsonl macbook_full.jsonl --out-json tuples.json

Notes:
- We compute post age relative to current time, based on post.created_utc.
- If the commenter karma parts are missing, user_total_karma is None.
- Output JSON is a list of 3-element arrays (JSON can't encode Python tuples natively).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

# Import from data.py

# Make the repository root importable when running this script directly
import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from backend.data import search_and_fetch
except Exception as e:
    raise SystemExit(f"Failed to import backend.data.search_and_fetch: {e}")

TupleType = Tuple[str, str, List[Union[int, float, None]]]


def _humanize_age(seconds_ago: float) -> str:
    """Return a compact human-readable age like '5m', '3h', '2d', '7mo', '1y'."""
    if seconds_ago < 0:
        seconds_ago = 0
    minutes = seconds_ago / 60.0
    hours = minutes / 60.0
    days = hours / 24.0
    months = days / 30.0
    years = days / 365.0
    if minutes < 1:
        return f"{int(seconds_ago)}s"
    if hours < 1:
        return f"{int(minutes)}m"
    if days < 1:
        return f"{int(hours)}h"
    if months < 1:
        return f"{int(days)}d"
    if years < 1:
        return f"{int(months)}mo"
    return f"{int(years)}y"


essential_comment_fields = ("body", "comment_url", "score", "author_link_karma", "author_comment_karma")


def build_comment_tuples_from_jsonl(in_jsonl: str) -> List[TupleType]:
    """
    Read a JSONL file produced by backend/data.py and return the array of tuples.

    Tuple fields:
      0: comment body (str)
      1: comment URL (str)
      2: details list [post_score, user_total_karma, comment_score, post_age_ago]
    """
    tuples: List[TupleType] = []
    now = time.time()

    with open(in_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec: Dict[str, Any] = json.loads(line)
            if "post" not in rec or "comments" not in rec:
                continue

            post = rec["post"]
            comments = rec["comments"] if isinstance(rec["comments"], list) else []

            post_score = int(post.get("score", 0))
            created_utc = float(post.get("created_utc", now))
            now_dt = datetime.now(timezone.utc)
            age_months = (now_dt - datetime.fromtimestamp(created_utc, timezone.utc)).total_seconds() / (86400.0 * 30.0)
            if age_months < (1.0 / 30.0):  # enforce minimum of 1 day expressed in months
                age_months = (1.0 / 30.0)

            for c in comments:
                # Some lines may be error records; skip those.
                if not isinstance(c, dict):
                    continue
                if "error" in c:
                    continue

                body = c.get("body")
                url = c.get("comment_url")
                if not body or not url:
                    # Only keep well-formed comment entries
                    continue

                comment_score = int(c.get("score", 0))
                link_k = c.get("author_link_karma")
                comm_k = c.get("author_comment_karma")

                user_total_karma: Optional[int]
                if isinstance(link_k, int) or isinstance(comm_k, int):
                    user_total_karma = int((link_k or 0) + (comm_k or 0))
                else:
                    user_total_karma = None

                details: List[Optional[int] | float] = [post_score, user_total_karma, comment_score, age_months]
                tuples.append((body, url, details))

    return tuples


def main() -> None:
    parser = argparse.ArgumentParser(description="Refactor JSONL from backend/data.py into tuples of (comment, url, [details]).")
    parser.add_argument("--in-jsonl", help="Input JSONL file produced by backend/data.py", required=False)
    parser.add_argument("--out-json", help="Output JSON file with list of tuples (as arrays)", required=False, default="tuples.json")

    # Optional end-to-end path: let the user pass a search query and generate a temp JSONL first
    parser.add_argument("--query", help="If set, run a search via backend.data.search_and_fetch and then refactor its JSONL.")
    parser.add_argument("--subreddit", default=None)
    parser.add_argument("--time-filter", default="all")
    parser.add_argument("--sort", default="relevance")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--comments", type=int, default=30)

    args = parser.parse_args()

    tmp_jsonl_path: Optional[str] = None

    if args.query:
        # produce a temporary JSONL using data.search_and_fetch
        tmp_jsonl_path = "_tmp_search_results.jsonl"
        search_and_fetch(
            query=args.query,
            subreddit=args.subreddit,
            sort=args.sort,
            time_filter=args.time_filter,
            limit=args.limit,
            max_comments=args.comments,
            posts_json_path="_tmp_search_meta.json",
            posts_jsonl_path=tmp_jsonl_path,
        )
        in_path = tmp_jsonl_path
    else:
        if not args.in_jsonl:
            raise SystemExit("Either --in-jsonl or --query is required.")
        in_path = args.in_jsonl

    tuples = build_comment_tuples_from_jsonl(in_path)

    # Convert tuples to lists for JSON output
    json_ready: List[List[Any]] = [ [t[0], t[1], t[2]] for t in tuples ]
    Path(args.out_json).write_text(json.dumps(json_ready, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[write] {len(json_ready)} tuples -> {args.out_json}")


if __name__ == "__main__":
    main()