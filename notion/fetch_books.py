import os
import httpx
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

async def fetch_books_by_status(status: str):
    async with httpx.AsyncClient() as client:
        query = {
            "filter": {
                "property": "Status",
                "select": {
                    "equals": status
                }
            }
        }
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = await client.post(url, headers=HEADERS, json=query)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
