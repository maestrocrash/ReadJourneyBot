import os
import httpx
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # В .env укажи ID базы

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

async def create_book_in_notion(title: str, author: str, status: str, year: int) -> bool:
    url = "https://api.notion.com/v1/pages"
    # Текущий год
    current_year = str(datetime.now().year)

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": title}}
                ]
            },
            "Author": {
                "select": {
                    "name": author
                }
            },
            "Status": {
                "select": {"name": status}
            },
            "Год": {
                "multi_select": [
                    { "name": current_year }
                ]
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            print(f"Ошибка создания книги: {response.status_code} — {response.text}")
            return False
