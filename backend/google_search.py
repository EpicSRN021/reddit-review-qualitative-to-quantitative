import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

def google_search(query: str, api_key: str, cse_id: str, num_results: int = 10) -> list[str]:
    """Perform a Google Custom Search and return a list of result URLs."""
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num_results).execute()
    return [item['link'] for item in res.get('items', [])]

def get_top_reddit_reviews(keyword: str, num_results: int = 10) -> list[str]:
    """Search for 'keyword review reddit' and return top Reddit URLs."""
    query = f"{keyword} review reddit site:reddit.com"
    return google_search(query, API_KEY, CSE_ID, num_results)

if __name__ == "__main__":
    kw = input("Enter keyword: ")
    urls = get_top_reddit_reviews(kw)
    print("\nTop Reddit Review URLs:")
    for url in urls:
        print(url)

