import os
import requests
from datetime import datetime, timedelta
from notion_client import Client

# =========================================================
# AUTH
# =========================================================
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
PAGE_ID = os.environ["NOTION_PAGE_ID"]

notion = Client(auth=NOTION_TOKEN)

# =========================================================
# TIME
# =========================================================
now = datetime.utcnow()
yesterday = now - timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")

# =========================================================
# TEMPERATURE
# =========================================================
def get_temperature():
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 69.590,
            "longitude": -139.099,
            "current_weather": True
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return {
            "temperature": data["current_weather"]["temperature"],
            "source": "Open-Meteo (ERA5 reanalysis)",
            "status": "ok"
        }

    except Exception:
        return {
            "temperature": None,
            "source": "fallback",
            "status": "missing"
        }

temp_data = get_temperature()

temp_text = (
    f"Current air temperature: {temp_data['temperature']} °C\n"
    f"Source: {temp_data['source']}\n"
    f"Status: {temp_data['status']}"
)

# =========================================================
# SATELLITE IMAGE (REAL EMBED)
# =========================================================
def get_satellite_image_url(date_str):
    bbox = "-141,68,-136,71"  # Herschel Island region

    return (
        "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
        "?service=WMS"
        "&request=GetMap"
        "&layers=MODIS_Terra_CorrectedReflectance_TrueColor"
        "&styles="
        "&format=image/png"
        f"&bbox={bbox}"
        "&width=1024"
        "&height=768"
        f"&time={date_str}"
    )

sat_img_url = get_satellite_image_url(date_str)

# =========================================================
# DASHBOARD BLOCKS
# =========================================================
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

    # TIME
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

    {"object": "block", "type": "divider", "divider": {}},

    # =====================================================
    # SATELLITE IMAGE (NOW REAL IMAGE BLOCK)
    # =====================================================
    {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "🛰 Satellite (MODIS True Color – Yesterday)"
                }
            }]
        }
    },

    {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": sat_img_url
            }
        }
    },

    # =====================================================
    # TEMPERATURE
    # =====================================================
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
                    "content": temp_text
                }
            }]
        }
    },

    # =====================================================
    # SEA ICE (placeholder)
    # =====================================================
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
                    "content": "Next: OSI SAF sea ice concentration integration."
                }
            }]
        }
    },

    # =====================================================
    # TIDES
    # =====================================================
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
                    "content": "DFO tide gauge (06525) + Copernicus sea level anomaly planned."
                }
            }]
        }
    }
]

# =========================================================
# CLEAR PAGE
# =========================================================
existing = notion.blocks.children.list(block_id=PAGE_ID)

for b in existing["results"]:
    notion.blocks.delete(block_id=b["id"])

# =========================================================
# UPDATE PAGE
# =========================================================
notion.blocks.children.append(
    block_id=PAGE_ID,
    children=blocks
)

print("Dashboard updated successfully")
