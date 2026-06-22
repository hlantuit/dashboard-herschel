import os
from datetime import datetime, timedelta
from notion_client import Client

# ----------------------------
# AUTH
# ----------------------------
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
PAGE_ID = os.environ["NOTION_PAGE_ID"]

notion = Client(auth=NOTION_TOKEN)

# ----------------------------
# TIME (Inuvik-based reference note)
# ----------------------------
now = datetime.utcnow()
yesterday = now - timedelta(days=1)

date_str = yesterday.strftime("%Y-%m-%d")

# Worldview fixed timestamp (approx midday Arctic observation window)
worldview_url = (
    "https://worldview.earthdata.nasa.gov/"
    f"?t={date_str}-T18%3A00%3A00Z"
)

# ----------------------------
# DASHBOARD CONTENT
# ----------------------------
blocks = [
    # TITLE
    {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Herschel Island Environmental Dashboard"
                }
            }]
        }
    },

    # TIMESTAMP
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": f"Last update (UTC): {now.strftime('%Y-%m-%d %H:%M')}"
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "divider",
        "divider": {}
    },

    # SATELLITE SECTION
    {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "🛰 Satellite (Worldview – previous day)"
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": f"Automated observation for {date_str} (Inuvik reference time)."
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": worldview_url
                }
            }]
        }
    },

    # TEMPERATURE (placeholder scientific structure)
    {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "🌡 Air Temperature"
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Data source: ECCC (Ivvavik / Herschel proxy station) + model fallback (Meteoblue / ERA5 planned)."
                }
            }]
        }
    },

    # SEA ICE
    {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "🧊 Sea Ice Conditions"
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Planned: OSI SAF sea ice concentration (satellite-derived). Backup: Canadian Ice Service products during open-water season."
                }
            }]
        }
    },

    # TIDES
    {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "🌊 Tides & Sea Level"
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Fisheries & Oceans Canada tide gauge (station 06525) + Copernicus sea level anomaly (planned integration)."
                }
            }]
        }
    },

    # FOOTER SCIENCE NOTE
    {
        "object": "block",
        "type": "divider",
        "divider": {}
    },

    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Note: All timestamps are reported in UTC; interpretation should be made relative to Inuvik local time (UTC−7 / UTC−8 depending on season)."
                }
            }]
        }
    }
]

# ----------------------------
# CLEAR PAGE
# ----------------------------
existing = notion.blocks.children.list(block_id=PAGE_ID)

for b in existing["results"]:
    notion.blocks.delete(block_id=b["id"])

# ----------------------------
# UPDATE PAGE
# ----------------------------
notion.blocks.children.append(
    block_id=PAGE_ID,
    children=blocks
)

print("Dashboard updated successfully")
