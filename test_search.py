import pytest
import time
import os
import json

from utils.api_client import search_api
from utils.extractor import extract_search_event_ids
from utils.schedule import fetch_full_schedule, process_epg_tiles, build_expected_events
from utils.generator import generate_sport_prompts_with_expected, generate_competition_prompts_with_expected, generate_contestant_prompts_with_expected


SPORT_RESULTS_FILE = "testdata/test_results_sports.txt"
COMPETITION_RESULTS_FILE = "testdata/test_results_competitions.txt"
CONTESTANT_RESULTS_FILE = "testdata/test_results_contestants.txt"
os.makedirs("testdata", exist_ok=True)


# ---------------------------------------
# 🔹 Fetch tiles ONCE (not fixture)
# ---------------------------------------
tiles = fetch_full_schedule(days_back=10, days_forward=2)
events = process_epg_tiles(tiles)
sport_prompts = generate_sport_prompts_with_expected(tiles)
competition_prompts = generate_competition_prompts_with_expected(tiles)
contestant_prompts = generate_contestant_prompts_with_expected(tiles)

# Save prompts to JSON files
os.makedirs("testdata", exist_ok=True)
with open("testdata/generated_sport_prompts.json", "w") as f:
    json.dump({"prompts": sport_prompts}, f, indent=4)
print(f"Saved {len(sport_prompts)} sport prompts to testdata/generated_sport_prompts.json")

with open("testdata/generated_competition_prompts.json", "w") as f:
    json.dump({"prompts": competition_prompts}, f, indent=4)
print(f"Saved {len(competition_prompts)} competition prompts to testdata/generated_competition_prompts.json")

with open("testdata/generated_contestant_prompts.json", "w") as f:
    json.dump({"prompts": contestant_prompts}, f, indent=4)
print(f"Saved {len(contestant_prompts)} contestant prompts to testdata/generated_contestant_prompts.json")

def load_schedule_sport_prompts(tiles):

    print(" GENERATING SPORT PROMPTS...")

    prompts_data = generate_sport_prompts_with_expected(tiles)

    os.makedirs("testdata", exist_ok=True)
    try:
        with open("testdata/generated_sport_prompts.json", "w") as f:
            json.dump({"prompts": prompts_data}, f, indent=4)

        print(f" Saved {len(prompts_data)} sport prompts to JSON")

    except Exception as e:
        print(f" Failed to write JSON: {e}")

    return prompts_data

def load_schedule_competition_prompts(tiles):

    print(" GENERATING COMPETITION PROMPTS...")

    prompts_data = generate_competition_prompts_with_expected(tiles)

    os.makedirs("testdata", exist_ok=True)
    try:
        with open("testdata/generated_competition_prompts.json", "w") as f:
            json.dump({"prompts": prompts_data}, f, indent=4)

        print(f" Saved {len(prompts_data)} competition prompts to JSON")

    except Exception as e:
        print(f" Failed to write JSON: {e}")

    return prompts_data


def load_schedule_contestant_prompts(tiles):

    print(" GENERATING CONTESTANT PROMPTS...")

    prompts_data = generate_contestant_prompts_with_expected(tiles)

    os.makedirs("testdata", exist_ok=True)
    try:
        with open("testdata/generated_contestant_prompts.json", "w") as f:
            json.dump({"prompts": prompts_data}, f, indent=4)

        print(f" Saved {len(prompts_data)} contestant prompts to JSON")

    except Exception as e:
        print(f" Failed to write JSON: {e}")

    return prompts_data
# ---------------------------------------
# 🔹 TEST SPORTS (parametrize)
# ---------------------------------------
@pytest.mark.parametrize("data", sport_prompts)
def test_search_with_schedule_sport_prompts(data):

    sport_id = data["sport_id"]
    sport_title = data["sport_title"]
    prompt = data["prompt"]

    print(f"\n==============================")
    print(f"Testing Sport: {sport_title}")
    print(f"Prompt: {prompt}")

    # -----------------------------------
    # 1️⃣ Call Search API
    # -----------------------------------
    start_time = time.time()
    response = search_api(prompt)
    response_time = round(time.time() - start_time, 2)

    search_data = extract_search_event_ids(response)
    search_article_ids = set(search_data["article_ids"])

    print(f"Search returned: {len(search_article_ids)} events")

    # -----------------------------------
    # 2️⃣ Build Expected
    # -----------------------------------
    expected_data = build_expected_events(events, sport_id=sport_id)
    expected_article_ids = set(expected_data["article_ids"])

    print(f"Expected events: {len(expected_article_ids)}")

    # -----------------------------------
    # 3️⃣ Compare
    # -----------------------------------
    missing = expected_article_ids - search_article_ids
    extra = search_article_ids - expected_article_ids
    print(f"Missing: {len(missing)}")
    print(f"Extra: {len(extra)}")

    if missing:
        print("Missing:", list(missing))

    if extra:
        print("Sample Extra:", list(extra)[:5])

    # -----------------------------------
    # 4️⃣ Assertion
    # -----------------------------------
    try:
        assert not missing, f"Missing events: {list(missing)}"

        result = "PASS"
        error_message = ""

    except AssertionError as e:
        result = "FAIL"
        error_message = str(e)

   
    #Logging
    # -----------------------------------
    if result == "FAIL":
     with open(file_Path2, "a") as f:
        f.write(
            f"\n==============================\n"
            f"SPORT: {sport_title}\n"
            f"PROMPT: {prompt}\n"
            f"TIME: {response_time}s\n"
            f"RESULT: {result}\n"
            f"MISSING COUNT: {len(missing)} events\n"
            f"MISSING EVENTS: {list(missing)}\n"
            f"EXTRA: {list(extra)}\n"
        )
        pytest.fail(error_message)


# =======================================
# 🔹 TEST COMPETITIONS (parametrize)
# =======================================
@pytest.mark.parametrize("data", competition_prompts)
def test_search_with_schedule_competition_prompts(data):

    competition_id = data["competition_id"]
    competition_title = data["competition_title"]
    prompt = data["prompt"]

    print(f"\n==============================")
    print(f"Testing Competition: {competition_title}")
    print(f"Prompt: {prompt}")

    # -----------------------------------
    # 1️⃣ Call Search API
    # -----------------------------------
    start_time = time.time()
    response = search_api(prompt)
    response_time = round(time.time() - start_time, 2)

    search_data = extract_search_event_ids(response)
    search_article_ids = set(search_data["article_ids"])

    print(f"Search returned: {len(search_article_ids)} events")

    # -----------------------------------
    # 2️⃣ Get expected from the data
    # -----------------------------------
    expected_article_ids = set(data["expected_article_ids"])

    print(f"Expected events: {len(expected_article_ids)}")

    # -----------------------------------
    # 3️⃣ Compare
    # -----------------------------------
    missing = expected_article_ids - search_article_ids
    extra = search_article_ids - expected_article_ids
    print(f"Missing: {len(missing)}")
    print(f"Extra: {len(extra)}")

    if missing:
        print("Missing:", list(missing))

    if extra:
        print("Sample Extra:", list(extra)[:5])

    # -----------------------------------
    # 4️⃣ Assertion
    # -----------------------------------
    try:
        assert not missing, f"Missing events: {list(missing)}"

        result = "PASS"
        error_message = ""

    except AssertionError as e:
        result = "FAIL"
        error_message = str(e)

    # Logging
    # -----------------------------------
    file_path_competitions = "testdata/test_results_competitions.txt"
    if result == "FAIL":
        with open(file_path_competitions, "a") as f:
            f.write(
                f"\n==============================\n"
                f"COMPETITION: {competition_title}\n"
                f"PROMPT: {prompt}\n"
                f"TIME: {response_time}s\n"
                f"RESULT: {result}\n"
                f"MISSING COUNT: {len(missing)} events\n"
                f"MISSING EVENTS: {list(missing)}\n"
                f"EXTRA: {list(extra)}\n"
            )
        pytest.fail(error_message)


# =======================================
# 🔹 TEST CONTESTANTS (parametrize)
# =======================================
@pytest.mark.parametrize("data", contestant_prompts)
def test_search_with_schedule_contestant_prompts(data):

    contestant_id = data["contestant_id"]
    contestant_title = data["contestant_title"]
    prompt = data["prompt"]

    print(f"\n==============================")
    print(f"Testing Contestant: {contestant_title}")
    print(f"Prompt: {prompt}")

    # -----------------------------------
    # 1️⃣ Call Search API
    # -----------------------------------
    start_time = time.time()
    response = search_api(prompt)
    response_time = round(time.time() - start_time, 2)

    search_data = extract_search_event_ids(response)
    search_article_ids = set(search_data["article_ids"])

    print(f"Search returned: {len(search_article_ids)} events")

    # -----------------------------------
    # 2️⃣ Get expected from the data
    # -----------------------------------
    expected_article_ids = set(data["expected_article_ids"])

    print(f"Expected events: {len(expected_article_ids)}")

    # -----------------------------------
    # 3️⃣ Compare
    # -----------------------------------
    missing = expected_article_ids - search_article_ids
    extra = search_article_ids - expected_article_ids
    print(f"Missing: {len(missing)}")
    print(f"Extra: {len(extra)}")

    if missing:
        print("Missing:", list(missing))

    if extra:
        print("Sample Extra:", list(extra)[:5])

    # -----------------------------------
    # 4️⃣ Assertion
    # -----------------------------------
    try:
        assert not missing, f"Missing events: {list(missing)}"

        result = "PASS"
        error_message = ""

    except AssertionError as e:
        result = "FAIL"
        error_message = str(e)

    # Logging
    # -----------------------------------
    file_path_contestants = "testdata/test_results_contestants.txt"
    if result == "FAIL":
        with open(file_path_contestants, "a") as f:
            f.write(
                f"\n==============================\n"
                f"CONTESTANT: {contestant_title}\n"
                f"PROMPT: {prompt}\n"
                f"TIME: {response_time}s\n"
                f"RESULT: {result}\n"
                f"MISSING COUNT: {len(missing)} events\n"
                f"MISSING EVENTS: {list(missing)}\n"
                f"EXTRA: {list(extra)}\n"
            )
        pytest.fail(error_message)