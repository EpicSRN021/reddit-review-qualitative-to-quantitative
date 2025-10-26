"""
backend/server.py - FIXED

HTTP server that exposes script.py to the frontend.
Run this with: python server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

# Import your existing script
from script import fetch_data

app = FastAPI()

# Allow frontend to make requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    keyword: str

@app.get("/")
def root():
    return {
        "status": "Server running ✓",
        "message": "POST to /analyze with {keyword: 'product_name'}"
    }

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Runs script.py's fetch_data() and returns formatted results
    """
    try:
        print(f"\n🔍 Analyzing: {request.keyword}")
        
        # Call your existing script.py function
        # Returns: (processed, final_score, final_metrics, summary_task)
        # where processed is list of [text, url, score, metrics, weight]
        processed, final_score, final_metrics, summary_task = await fetch_data(request.keyword)
        
        # Handle summary (might be a coroutine)
        if asyncio.iscoroutine(summary_task):
            summary = await summary_task
        else:
            summary = summary_task
        
        # Check if we have empty data (no Reddit comments found)
        if not processed or len(processed) == 0:
            print(f"✓ GPT Summary generated for '{request.keyword}' (no Reddit data available)")
            return {
                "final_rating": 0.0,              # No rating available
                "subscores": [0.0, 0.0, 0.0, 0.0], # No subscores available
                "ai_summary": summary,            # GPT-generated summary
                "comments": []                    # No comments available
            }
        
        print(f"✓ Analysis complete! Score: {final_score:.2f}/5.0")
        
        # Extract top 5 comments from processed
        # processed is sorted by weight, so just take first 5
        # Each item is [text, url, score, metrics, weight]
        top_comments = [[item[0], item[1]] for item in processed[:5]]
        
        # Return in format frontend expects
        return {
            "final_rating": final_score,      # double
            "subscores": final_metrics,       # [quality, cost, availability, utility]
            "ai_summary": summary,            # string
            "comments": top_comments          # [[text, url], [text, url], ...]
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"\n❌ Error: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting ReviewRadar Backend Server")
    print("="*60)
    print("Server will run on: http://localhost:8000")
    print("Frontend should connect to this URL")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)