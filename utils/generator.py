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
    sport_map = defaultdict(lambda: {
        "sport_titles": set(),
        "sport_event_ids": set()
    })

    print(f"DEBUG → Tiles count: {len(tiles)}")

    for i, tile in enumerate(tiles):
        sport = tile.get("Sport") or tile.get("sport") or {}
        sport_id = sport.get("Id")
        sport_title = sport.get("Title")
        event_id = tile.get("EventId")

        if not sport_id or not sport_title:
            print(f"[{i}] Skipped → Missing sport_id/title")
            continue

        clean_title = sport_title.strip()

        if clean_title:
            sport_map[sport_id]["sport_titles"].add(clean_title)

        if event_id:
            sport_map[sport_id]["sport_event_ids"].add(event_id)

    print(f"DEBUG → sports found: {len(sport_map)}")

    prompts_data = []

    for sport_id, data in sport_map.items():
        print(f"Sport ID: {sport_id}, Titles: {data['sport_titles']}")

        for title in data["sport_titles"]:
            prompts_data.append({
                "sport_id": sport_id,
                "sport_title": title,
                "prompt": f"show me {title} events",
                "expected_event_ids": list(data["sport_event_ids"])
            })

    print(f"DEBUG → prompts generated: {len(prompts_data)}")

    return prompts_data