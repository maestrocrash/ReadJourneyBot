import os
import httpx
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

async def update_book_in_notion(book_id: str, properties: dict) -> bool:
    url = f"https://api.notion.com/v1/pages/{book_id}"
    payload = {"properties": properties}

    async with httpx.AsyncClient() as client:
        response = await client.patch(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка обновления: {response.status_code} — {response.text}")
            return False
