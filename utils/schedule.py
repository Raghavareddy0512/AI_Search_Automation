import datetime
from email import utils
import json
import re
import requests
from utils.generator import generate_title_prompts

EPG_URL = "https://epg.discovery.indazn.com/eu/v5/epgWithDatesRange"


def schedule_api(
        country="ca",
        languageCode="en",
        startDate="2026-03-05",
        endDate="2026-03-11",
        timeZoneOffset=-300,
        brand="dazn"
):

    params = {
        "country": country,
        "languageCode": languageCode,
        "openBrowse": "false",
        "timeZoneOffset": timeZoneOffset,
        "startDate": startDate,
        "endDate": endDate,
        "brand": brand
    }

    response = requests.get(EPG_URL, params=params)
    response.raise_for_status()

    return response.json()


def extract_schedule_ids(schedule_json):

    schedule_ids = set()

    if isinstance(schedule_json, list):
        tiles = schedule_json
    elif isinstance(schedule_json, dict):
        tiles = schedule_json.get("Tiles", [])
    else:
        return schedule_ids

    for tile in tiles:
        if not isinstance(tile, dict):
            continue

        asset_id = tile.get("AssetId") or tile.get("assetId") or tile.get("assetID")
        if asset_id:
            schedule_ids.add(asset_id)

        related_ids = tile.get("RelatedIds") or tile.get("Related", [])
        if isinstance(related_ids, list):
            for rid in related_ids:
                if isinstance(rid, dict):
                    rid_val = rid.get("AssetId") or rid.get("assetId")
                    if rid_val:
                        schedule_ids.add(rid_val)
                elif rid:
                    schedule_ids.add(rid)

    return schedule_ids


#  UPDATED: returns title + guid (CRITICAL)
def extract_schedule_two_days(
        country="ca",
        languageCode="en",
        days_back=2,
        days_forward=2,
        timeZoneOffset=-300,
        brand="dazn"
):

    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days_back)
    end_date = today + datetime.timedelta(days=days_forward)

    schedule_json = schedule_api(
        country=country,
        languageCode=languageCode,
        startDate=start_date.isoformat(),
        endDate=end_date.isoformat(),
        timeZoneOffset=timeZoneOffset,
        brand=brand
    )

    events = []
    tiles = schedule_json.get("Tiles", [])

    for tile in tiles:
        if not isinstance(tile, dict):
            continue

        title = (
            tile.get("Title")
            or tile.get("title")
            or tile.get("Name")
            or tile.get("name")
        )

        asset_id = tile.get("AssetId") or tile.get("assetId")

        if title and asset_id:
            events.append({
                "title": title.strip(),
                "guid": asset_id
            })

    print(f"Fetched {len(events)} events from API.")
    try:
        with open("testdata/epg_events.json", "w") as f:
            json.dump({"events": events}, f, indent=4)
        print("EPG events saved to testdata/epg_events.json")
    except Exception as e:
        print(f"Failed to write JSON: {e}")

    return events



# def fetch_full_schedule(
#         country="ca",
#         languageCode="en",
#         days_back=90,
#         days_forward=90,
#         timeZoneOffset=-300,
#         brand="dazn"
# ):

#     try:
#         with open("full_schedule.json", "r") as f:
#             data = json.load(f)
#             tiles = data.get("Tiles", [])
#             if tiles:
#                 print(f"Loaded schedule data from file ({len(tiles)} tiles).")
#                 return tiles
#     except FileNotFoundError:
#         pass

#     print("Fetching full schedule from API...")

#     today = datetime.date.today()
#     start_date = today - datetime.timedelta(days=days_back)
#     end_date = today + datetime.timedelta(days=days_forward)

#     schedule_json = schedule_api(
#         country=country,
#         languageCode=languageCode,
#         startDate=start_date.isoformat(),
#         endDate=end_date.isoformat(),
#         timeZoneOffset=timeZoneOffset,
#         brand=brand
#     )

#     tiles = schedule_json.get("Tiles", [])

#     with open("full_schedule.json", "w") as f:
#         json.dump({"Tiles": tiles}, f, indent=4)

#     print(f"Saved schedule ({len(tiles)} tiles)")

#     return tiles