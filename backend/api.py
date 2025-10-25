from fastapi import FastAPI, Query, HTTPException
import os
from backend.data import fetch_post_data
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "endpoints": ["/post?url_or_id=<reddit_url_or_id>"]}

@app.get("/debug/env")
def debug_env():
    import os as _os
    cid = _os.getenv("REDDIT_CLIENT_ID") or ""
    ua = _os.getenv("REDDIT_USER_AGENT") or ""
    # mask client_id for safety, show only first/last 3 chars
    def mask(s: str) -> str:
        if len(s) <= 6:
            return "***"
        return f"{s[:3]}***{s[-3:]}"
    return {
        "client_id": mask(cid),
        "user_agent": ua,
        "has_secret": bool(_os.getenv("REDDIT_CLIENT_SECRET")),
    }

@app.get("/post")
def post(url_or_id: str = Query(..., description="Reddit URL or base36 ID"),
         max_comments: int = 100):
    try:
        return fetch_post_data(url_or_id, max_comments=max_comments)
    except Exception as e:
        # Return explicit error message for easier debugging (e.g., 401 due to env/creds)
        raise HTTPException(status_code=500, detail=f"Failed to fetch post: {e}")