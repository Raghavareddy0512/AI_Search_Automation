import json
from utils.schedule import fetch_full_schedule



if __name__ == "__main__":
    data = fetch_full_schedule()

    # print("\nSample upcoming IDs:", data["upcoming"]["assetTypeId":"sportId"])
    # print("\nSample live IDs:", data["live"]["assetTypeId":"sportId"])
    # print("\nSample catchup IDs:", data["catchup"]["assetTypeId":"sportId"])
    print("\n=== LIVE EVENTS ===")
    for item in data["live"]:
        print(
            f"EventId: {item['event_id']} | "
            f"AssetType: {item['assetTypeId']} | "
            f"Sport: {item['sportId']}"
        )