import datetime
import json

import requests

EPG_URL = "https://epg.discovery.indazn.com/eu/v5/epgWithDatesRange"


def schedule_api(
        country="ca",
        languageCode="en",
        startDate="2026-03-11",
        endDate="2026-03-17",
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
    tiles = schedule_json.get("Tiles", [])
    for tile in tiles:
        event_id = tile.get("AssetId") or tile.get("assetId") 
       
    return schedule_ids


def fetch_full_schedule(country="ca", languageCode="en", days_back=90, days_forward=90, timeZoneOffset=-300, brand="dazn"):
    """
    Loads the full EPG schedule data from full_schedule.json.
    If the file doesn't exist, fetches from API in 7-day chunks and stores it.
    """
    # Try to load from existing JSON file first
    try:
        with open("full_schedule.json", "r") as f:
            data = json.load(f)
            tiles = data.get("Tiles", [])
            if tiles:
                print(f"Loaded schedule data from full_schedule.json with {len(tiles)} tiles.")
                return tiles
    except FileNotFoundError:
        pass
    
    # If file doesn't exist, fetch from API
    print("full_schedule.json not found. Fetching from API...")
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days_back)
    end_date = today + datetime.timedelta(days=days_forward)
    
    all_tiles = []
    current_start = start_date
    
    while current_start < end_date:
        current_end = min(current_start + datetime.timedelta(days=6), end_date)
        
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
            assetID = tile.get("AssetId") or tile.get("assetId")
            # print("assetID: ", assertID)
            all_tiles.append(assetID)
        
        current_start = current_end + datetime.timedelta(days=1)
    
    # Store the full schedule data to a JSON file
    full_schedule_data = {"Tiles": all_tiles}
    with open("full_schedule.json", "w") as f:
        json.dump(full_schedule_data, f, indent=4)
    
    print(f"Full schedule data fetched and stored in full_schedule.json with {len(all_tiles)} tiles.")
    return all_tiles


