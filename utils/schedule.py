import datetime
from email import utils
import json
import os
import re
from tracemalloc import start
import requests
from utils.generator import generate_title_prompts
from utils.extractor import ASSET_TYPES

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

    MAX_RANGE = 6  #  safe chunk (7 days max)

    events = []
    seen_guids = set()
    seen_eventIds = set()
    seen_sportIds = set()
    seen_competitionIds = set()
    seen_contestantIds = set()

    current_start = start_date

    while current_start <= end_date:
        current_end = min(
            current_start + datetime.timedelta(days=MAX_RANGE),
            end_date
        )

        print(f"Fetching EPG: {current_start} → {current_end}")

        try:
            schedule_json = schedule_api(
                country=country,
                languageCode=languageCode,
                startDate=current_start.isoformat(),
                endDate=current_end.isoformat(),
                timeZoneOffset=timeZoneOffset,
                brand=brand
            )
        except Exception as e:
            print(f"API failed for {current_start} → {current_end}: {e}")
            current_start = current_end + datetime.timedelta(days=1)
            continue

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
            event_id = tile.get("EventId") or tile.get("eventId")
            sport_obj = tile.get("Sport") or tile.get("sport") or {}
            sport_id = sport_obj.get("Id")
            sport_name = sport_obj.get("Title")
            start_date = tile.get("Start") or tile.get("start")
            article_type = tile.get ("AssetTypeId") or tile.get("assetTypeId")
            if title and asset_id and asset_id not in seen_guids:
                seen_guids.add(asset_id)
                seen_eventIds.add(event_id)
                seen_sportIds.add(sport_id)
                seen_competitionIds.add(tile.get("CompetitionId"))
                seen_contestantIds.update(tile.get("ContestantIds", []))

                events.append({
                    "title": title.strip(),
                    "guid": asset_id,
                    "event_id": event_id,
                    "sport_id": sport_id,
                    "sport": sport_name,
                    "start_date": start_date,
                    "article_type": article_type

                })

        current_start = current_end + datetime.timedelta(days=1)

    print(f"Fetched {len(events)} events from API.")

    try:
        with open("testdata/epg_events.json", "w") as f:
            json.dump({"events": events}, f, indent=4)
        print("EPG events saved to testdata/epg_events.json")
    except Exception as e:
        print(f"Failed to write JSON: {e}")

    return events




#  ---Modify for any date range ----

# def fetch_full_schedule(
#     country="ca",
#     languageCode="en",
#     days_back=10,
#     days_forward=2,
#     timeZoneOffset=-300,
#     brand="dazn"
# ):

#     file_path = "testdata/full_schedule.json"

#     # Step 1: Load from cache
#     if os.path.exists(file_path):
#         with open(file_path, "r") as f:
#             data = json.load(f)
#             tiles = data.get("Tiles", [])
#             if tiles:
#                 print(f"Loaded schedule from file ({len(tiles)} tiles).")
#                 return tiles

#     print("Fetching schedule from API (chunked)...")

#     today = datetime.date.today()
#     start_date = today - datetime.timedelta(days=days_back)
#     end_date = today + datetime.timedelta(days=days_forward)

#     MAX_RANGE = 6  #  API-safe chunk
#     EPG_ASSET_TYPES = {
#         "LIVE": "19bajo019znum1tkhzn0qz6iy4",
#         "UPCOMING": "1f2vso6mwht2x1x9hi3euru0fb",
#         "CATCHUP": "1k7t7oc0q1omt19gij7s3hc676",
#         "HIGHLIGHT": "1dpp4008gvoq81nbxq0iu9x2jv"
#     }
#     all_tiles = []
#     EPG_live = []
#     EPG_upcoming = []
#     EPG_catchup = []
#     EPG_highlights = []

#     seen_ids = set()

#     current_start = start_date

#     while current_start <= end_date:
#         current_end = min(
#             current_start + datetime.timedelta(days=MAX_RANGE),
#             end_date
#         )

#         print(f"Fetching: {current_start} → {current_end}")

#         try:
#             schedule_json = schedule_api(
#                 country=country,
#                 languageCode=languageCode,
#                 startDate=current_start.isoformat(),
#                 endDate=current_end.isoformat(),
#                 timeZoneOffset=timeZoneOffset,
#                 brand=brand
#             )
#         except Exception as e:
#             print(f"API failed for {current_start} → {current_end}: {e}")
#             current_start = current_end + datetime.timedelta(days=1)
#             continue

#         tiles = schedule_json.get("Tiles", [])

#         for tile in tiles:
#             asset_id = tile.get("AssetId") or tile.get("assetId")
#             EPG_guid = tile.get("Id") or tile.get("AssetId")
#             EPG_event_id = tile.get("EventId") or tile.get("eventId")
#             EPG_sport_obj = tile.get("Sport") or tile.get("sport") or {}
#             EPG_sport_id = EPG_sport_obj.get("Id")
#             EPG_sport_name = EPG_sport_obj.get("Title")
#             asset_type = tile.get("AssetTypeId") or tile.get("assetTypeId")

#             if not EPG_event_id or not asset_type:
#                     continue

#             all_tiles.append(EPG_event_id)
#             print(f"DEBUG → Found event: {EPG_event_id} (Sport: {EPG_sport_name}, AssetType: {asset_type})")

#             if asset_type == ASSET_TYPES["LIVE"]:
#                     EPG_live.append(EPG_event_id)

#             elif asset_type == ASSET_TYPES["UPCOMING"]:
#                     EPG_upcoming.append(EPG_event_id)

#             elif asset_type == ASSET_TYPES["CATCHUP"]:
#                     EPG_catchup.append(EPG_event_id)

#             elif asset_type == ASSET_TYPES["HIGHLIGHT"]:
#                     EPG_highlights.append(EPG_event_id)

#             if asset_id and asset_id not in seen_ids:
#                 seen_ids.add(asset_id)
#                 all_tiles.append(tile)

#         current_start = current_end + datetime.timedelta(days=1)

#     #  Save to file
#     with open(file_path, "w") as f:
#         json.dump({"Tiles": all_tiles}, f, indent=4)

#     return all_tiles



import datetime
import json
import requests

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


def fetch_full_schedule(
    country="ca",
    languageCode="en",
    days_back=10,
    days_forward=2,
    timeZoneOffset=-300,
    brand="dazn"
):

    EPG_ASSET_TYPES = {
        "LIVE": "19bajo019znum1tkhzn0qz6iy4",
        "UPCOMING": "1f2vso6mwht2x1x9hi3euru0fb",
        "CATCHUP": "1k7t7oc0q1omt19gij7s3hc676",
        "HIGHLIGHT": "1dpp4008gvoq81nbxq0iu9x2jv"
    }

    grouped = {
        "live": set(),
        "upcoming": set(),
        "catchup": set(),
        "highlight": set(),
        "all_assets": set(),
        "all_events": set(),
        "all_sports": set(),
        "all_sport_names": set()
    }

    all_tiles = []  # ✅ IMPORTANT FIX

    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days_back)
    end_date = today + datetime.timedelta(days=days_forward)

    MAX_RANGE = 6
    current_start = start_date

    while current_start <= end_date:

        current_end = min(
            current_start + datetime.timedelta(days=MAX_RANGE),
            end_date
        )

        print(f"Fetching: {current_start} → {current_end}")

        schedule_json = schedule_api(
            country=country,
            languageCode=languageCode,
            startDate=current_start.isoformat(),
            endDate=current_end.isoformat(),
            timeZoneOffset=timeZoneOffset,
            brand=brand
        )

        tiles = schedule_json.get("Tiles", [])

        for tile in tiles:
            all_tiles.append(tile)  # ✅ STORE RAW TILE

            asset_id = tile.get("AssetId") or tile.get("assetId")
            epg_event_id = tile.get("EventId") or tile.get("eventId")
            epg_sport_obj = tile.get("Sport") or tile.get("sport") or {}
            epg_sport_id = epg_sport_obj.get("Id")
            epg_sport_name = epg_sport_obj.get("Title") or epg_sport_obj.get("Name")
            asset_type = tile.get("AssetTypeId") or tile.get("assetTypeId")

            if not asset_id or not asset_type:
                continue

            grouped["all_assets"].add(asset_id)
            if epg_event_id:
                grouped["all_events"].add(epg_event_id)
            if epg_sport_id:
                grouped["all_sports"].add(epg_sport_id)
            if epg_sport_name:
                grouped["all_sport_names"].add(epg_sport_name)

            # classify
            if asset_type == EPG_ASSET_TYPES["LIVE"]:
                grouped["live"].add(asset_id)

            elif asset_type == EPG_ASSET_TYPES["UPCOMING"]:
                grouped["upcoming"].add(asset_id)

            elif asset_type == EPG_ASSET_TYPES["CATCHUP"]:
                grouped["catchup"].add(asset_id)

            elif asset_type == EPG_ASSET_TYPES["HIGHLIGHT"]:
                grouped["highlight"].add(asset_id)

        current_start = current_end + datetime.timedelta(days=1)

    # Debug summary
    print("\n===== EPG CLASSIFICATION =====")
    print(f"Total Tiles: {len(all_tiles)}")  # ✅ NEW
    print(f"Total Assets: {len(grouped['all_assets'])}")
    print(f"Total Events: {len(grouped['all_events'])}")
    print(f"Total Sports: {len(grouped['all_sports'])}")
    print(f"Total Sport Names: {len(grouped['all_sport_names'])}")
    print(f"Live: {len(grouped['live'])}")
    print(f"Upcoming: {len(grouped['upcoming'])}")
    print(f"Catchup: {len(grouped['catchup'])}")
    print(f"Highlight: {len(grouped['highlight'])}")

    # ✅ FINAL RETURN FIX
    return {
        "Tiles": all_tiles,
        **{k: list(v) for k, v in grouped.items()}
    }