import os
from notion_client import Client
from datetime import datetime

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
PAGE_ID = os.environ["NOTION_PAGE_ID"]

notion = Client(auth=NOTION_TOKEN)

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

notion.pages.update(
    page_id=PAGE_ID,
    properties={
        "title": {
            "title": [
                {
                    "text": {
                        "content": f"Herschel Dashboard (updated {now})"
                    }
                }
            ]
        }
    }
)

print("SUCCESS: Notion updated")
