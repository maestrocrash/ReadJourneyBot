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

async def fetch_authors() -> list[str]:
    authors = set()
    has_more = True
    next_cursor = None

    async with httpx.AsyncClient() as client:
        while has_more:
            query = {
                "page_size": 100,
            }
            if next_cursor:
                query["start_cursor"] = next_cursor

            url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            response = await client.post(url, headers=HEADERS, json=query)
            response.raise_for_status()
            data = response.json()

            for result in data.get("results", []):
                props = result.get("properties", {})
                author_select = props.get("Author", {}).get("select")
                if author_select and author_select.get("name"):
                    authors.add(author_select["name"])

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor", None)

    return sorted(authors)

