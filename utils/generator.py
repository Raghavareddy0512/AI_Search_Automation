import re
from urllib import response
from collections import defaultdict

def generate_title_prompts(title):
    title = title.strip()
    if not title:
        return []

    prompts = [title]  # Always include full title

    # --- Step 1: Split by "|" ---
    pipe_parts = [p.strip() for p in title.split("|") if p.strip()]

    if len(pipe_parts) > 1:
        left_part = pipe_parts[0]
        right_part = pipe_parts[1]

        prompts.append(left_part)
        prompts.append(right_part)
    else:
        left_part = title

    # --- Step 2: Split by ":" ---
    colon_parts = [p.strip() for p in left_part.split(":") if p.strip()]

    if len(colon_parts) > 1:
        match_part = colon_parts[0]
        suffix_part = colon_parts[1]

        prompts.append(match_part)
        prompts.append(suffix_part)
    else:
        match_part = left_part

    # --- Step 3: Split match_part (A vs B OR A - B) ---
    separator_pattern = r"\s+(?:vs\.?|[-])\s+"
    match = re.search(separator_pattern, match_part, flags=re.IGNORECASE)

    if match:
        left = match_part[:match.start()].strip()
        right = match_part[match.end():].strip()

        if left:
            prompts.append(left)
        if right:
            prompts.append(right)

    # --- Remove duplicates (preserve order) ---
    seen = set()
    final_prompts = []
    for p in prompts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            final_prompts.append(p)

    return final_prompts


def generate_sport_prompts_with_expected(tiles):

    EPG_ASSET_TYPES = {
        "UPCOMING": "1f2vso6mwht2x1x9hi3euru0fb",
        "CATCHUP": "1k7t7oc0q1omt19gij7s3hc676",
        "HIGHLIGHT": "1dpp4008gvoq81nbxq0iu9x2jv"
    }

    sport_map = defaultdict(lambda: {
        "sport_titles": set(),
        "upcoming": [],
        "catchup": [],
        "highlight": []
    })

    print(f"DEBUG → Tiles count: {len(tiles)}")

    # -----------------------------------
    # 1️⃣ Group by sport + asset type
    # -----------------------------------
    for i, tile in enumerate(tiles):

        sport = tile.get("Sport") or tile.get("sport") or {}
        sport_id = sport.get("Id")
        sport_title = sport.get("Title") or sport.get("Name")

        article_id = tile.get("AssetId") or tile.get("assetId")
        event_id = tile.get("EventId") or tile.get("eventId")
        asset_type = tile.get("AssetTypeId") or tile.get("assetTypeId")
        start_date = tile.get("Start") or tile.get("start")

        if not sport_id or not sport_title or not article_id:
            continue

        clean_title = sport_title.strip()
        sport_map[sport_id]["sport_titles"].add(clean_title)

        event_obj = {
            "article_id": article_id,
            "event_id": event_id,
            "start_date": start_date
        }

        if asset_type == EPG_ASSET_TYPES["UPCOMING"]:
            sport_map[sport_id]["upcoming"].append(event_obj)

        elif asset_type == EPG_ASSET_TYPES["CATCHUP"]:
            sport_map[sport_id]["catchup"].append(event_obj)

        elif asset_type == EPG_ASSET_TYPES["HIGHLIGHT"]:
            sport_map[sport_id]["highlight"].append(event_obj)

    print(f"DEBUG → sports found: {len(sport_map)}")

    prompts_data = []

    # -----------------------------------
    # 2️⃣ Build expected per sport
    # -----------------------------------
    for sport_id, data in sport_map.items():

        # 🔥 Sort by latest first
        data["upcoming"].sort(key=lambda x: x["start_date"] or "", reverse=True)
        data["catchup"].sort(key=lambda x: x["start_date"] or "", reverse=True)
        data["highlight"].sort(key=lambda x: x["start_date"] or "", reverse=True)

        limit = 50

        # -----------------------------------
        # Upcoming
        # -----------------------------------
        expected_upcoming = [
            e["article_id"] for e in data["upcoming"][:limit]
        ]

        remaining = limit - len(expected_upcoming)

        # -----------------------------------
        # Catchup
        # -----------------------------------
        expected_catchup = []
        if remaining > 0:
            expected_catchup = [
                e["article_id"] for e in data["catchup"][:remaining]
            ]
            remaining -= len(expected_catchup)

        # -----------------------------------
        # Highlight
        # -----------------------------------
        expected_highlight = []
        if remaining > 0:
            expected_highlight = [
                e["article_id"] for e in data["highlight"][:remaining]
            ]

        # -----------------------------------
        # Combined expected
        # -----------------------------------
        expected_article_ids = (
            expected_upcoming
            + expected_catchup
            + expected_highlight
        )

        # -----------------------------------
        # Create prompts
        # -----------------------------------
        for title in data["sport_titles"]:

            prompts_data.append({
                "sport_id": sport_id,
                "sport_title": title,
                "prompt": f"show me {title} events",

                # ✅ FULL expected breakdown
                "expected_article_ids": expected_article_ids,
                "expected_upcoming": expected_upcoming,
                "expected_catchup": expected_catchup,
                "expected_highlight": expected_highlight
            })

    print(f"DEBUG → prompts generated: {len(prompts_data)}")

    return prompts_data




def generate_competition_prompts_with_expected(tiles):
    
    EPG_ASSET_TYPES = {
        "UPCOMING": "1f2vso6mwht2x1x9hi3euru0fb",
        "CATCHUP": "1k7t7oc0q1omt19gij7s3hc676",
        "HIGHLIGHT": "1dpp4008gvoq81nbxq0iu9x2jv"
    }

    competition_map = defaultdict(lambda: {
        "competition_titles": set(),
        "upcoming": [],
        "catchup": [],
        "highlight": []
    })

    print(f"DEBUG → Tiles count: {len(tiles)}")

    # -----------------------------------
    # 1️⃣ Group by competition + asset type
    # -----------------------------------
    for i, tile in enumerate(tiles):

        competition = tile.get("Competition") or tile.get("competition") or {}
        competition_id = competition.get("Id")
        competition_title = competition.get("Title") or competition.get("Name")

        article_id = tile.get("AssetId") or tile.get("assetId")
        event_id = tile.get("EventId") or tile.get("eventId")
        asset_type = tile.get("AssetTypeId") or tile.get("assetTypeId")
        start_date = tile.get("Start") or tile.get("start")

        if not competition_id or not competition_title or not article_id:
            continue

        clean_title = competition_title.strip()
        competition_map[competition_id]["competition_titles"].add(clean_title)

        event_obj = {
            "article_id": article_id,
            "event_id": event_id,
            "start_date": start_date
        }

        if asset_type == EPG_ASSET_TYPES["UPCOMING"]:
            competition_map[competition_id]["upcoming"].append(event_obj)

        elif asset_type == EPG_ASSET_TYPES["CATCHUP"]:
            competition_map[competition_id]["catchup"].append(event_obj)

        elif asset_type == EPG_ASSET_TYPES["HIGHLIGHT"]:
            competition_map[competition_id]["highlight"].append(event_obj)

    print(f"DEBUG → competitions found: {len(competition_map)}")

    prompts_data = []

    # -----------------------------------
    # 2️⃣ Build expected per competition
    # -----------------------------------
    for competition_id, data in competition_map.items():

        # 🔥 Sort by latest first
        data["upcoming"].sort(key=lambda x: x["start_date"] or "", reverse=True)
        data["catchup"].sort(key=lambda x: x["start_date"] or "", reverse=True)
        data["highlight"].sort(key=lambda x: x["start_date"] or "", reverse=True)

        limit = 50

        # -----------------------------------
        # Upcoming
        # -----------------------------------
        expected_upcoming = [
            e["article_id"] for e in data["upcoming"][:limit]
        ]

        remaining = limit - len(expected_upcoming)

        # -----------------------------------
        # Catchup
        # -----------------------------------
        expected_catchup = []
        if remaining > 0:
            expected_catchup = [
                e["article_id"] for e in data["catchup"][:remaining]
            ]
            remaining -= len(expected_catchup)

        # -----------------------------------
        # Highlight
        # -----------------------------------
        expected_highlight = []
        if remaining > 0:
            expected_highlight = [
                e["article_id"] for e in data["highlight"][:remaining]
            ]

        # -----------------------------------
        # Combined expected
        # -----------------------------------
        expected_article_ids = (
            expected_upcoming
            + expected_catchup
            + expected_highlight
        )

        # -----------------------------------
        # Create prompts
        # -----------------------------------
        for title in data["competition_titles"]:

            prompts_data.append({
                "competition_id": competition_id,
                "competition_title": title,
                "prompt": f"show me {title} events",

                # ✅ FULL expected breakdown
                "expected_article_ids": expected_article_ids,
                "expected_upcoming": expected_upcoming,
                "expected_catchup": expected_catchup,
                "expected_highlight": expected_highlight
            })

    print(f"DEBUG → competition prompts generated: {len(prompts_data)}")

    return prompts_data