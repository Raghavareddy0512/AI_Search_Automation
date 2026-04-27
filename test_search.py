import pytest
import json
import time

from utils.api_client import search_api
from utils.extractor import extract_dates, extract_search_event_ids, extract_dates
from utils.schedule import (
    extract_schedule_two_days,
    fetch_full_schedule
)
from utils.generator import generate_title_prompts, generate_sport_prompts_with_expected
from utils.validator import has_date_intent, is_day_stage_pattern
# ------------------ OPTIONAL / NOT NEEDED FOR NOW ------------------

# import json
# from utils.extractor import extract_article_types, extract_guids, extract_strategy, extract_category
# from utils.schedule import schedule_api, extract_schedule_ids
# from utils.validator import validate_list

# @pytest.fixture(scope="session")
# def schedule_ids():
#     # ❌ Not needed anymore (we validate directly with GUID)
#     pass

# def load_tests():
#     # ❌ Static JSON-based tests not needed for dynamic flow
#     pass


# ------------------ DYNAMIC DATA GENERATION ------------------

def load_schedule_title_prompts():
    """
    EPG → title + GUID → generate prompts
    """
    data = []
    generated_prompts = []
    events = extract_schedule_two_days(days_back=10, days_forward=2)
    full_Events = fetch_full_schedule(days_back=10, days_forward=2)

    for event in events:
        title = event["title"]
        guid = event["guid"]
        event_id = event["event_id"]

        prompts = generate_title_prompts(title)

        for prompt in prompts:
            record = {
                "title": title,
                "prompt": prompt,
                "expected_guid": guid,
                "expected_event_id": event_id
                # "expectedStartDate": event.get("startDate"), # type: ignore
                # "expectedEndDate": event.get("endDate")
            }
            
            data.append(record)
            generated_prompts.append(record)
    try:
        with open("testdata/generated_prompts.json", "w") as f:
            json.dump({"prompts": generated_prompts}, f, indent=4)
        print(f"Saved {len(generated_prompts)} prompts to testdata/generated_prompts.json")
    except Exception as e:
        print(f"Failed to write prompts JSON: {e}")
    return data


def load_schedule_sport_prompts():
    """
    EPG → sport titles → generate prompts + expected event_ids
    """
    sports_data = []
    sports_generated_prompts = []

    schedule_json = fetch_full_schedule(days_back=10, days_forward=2)
    tiles = schedule_json.get("Tiles", [])

    prompts_data = generate_sport_prompts_with_expected(tiles)

    for item in prompts_data:
        record = {
            "sport_id": item["sport_id"],
            "sport_title": item["sport_title"],
            "prompt": item["prompt"],
            "expected_event_ids": item["expected_event_ids"]
        }

        sports_data.append(record)
        sports_generated_prompts.append(record)

    # Write to JSON
    try:
        with open("testdata/generated_sport_prompts.json", "w") as f:
            json.dump({"prompts": sports_generated_prompts}, f, indent=4)
        print(f"Saved {len(sports_generated_prompts)} sport prompts to testdata/generated_sport_prompts.json")
    except Exception as e:
        print(f"Failed to write sport prompts JSON: {e}")

    return sports_data

# ------------------ MAIN TEST (DYNAMIC + STRONG VALIDATION ) ------------------
file_path = "testdata/test_results.txt"
file_Path2 = "testdata/test_results_sports.txt"

# @pytest.mark.parametrize("data", load_schedule_title_prompts())
# def test_search_with_schedule_title_prompts(data):

#     title = data["title"]
#     prompt = data["prompt"]
#     expected_guid = data["expected_guid"]
#     expected_event_id = data["expected_event_id"]

#     print(f"\nTesting Title: {title}")
#     print(f"Prompt: {prompt}")

#     start_time = time.time()
#     response = search_api(prompt)
#     response_time = round(time.time() - start_time, 2)
#     search_data = extract_search_event_ids(response)
#     search_event_ids = set(
#     search_data["live_ids"]
#     + search_data["upcoming_ids"]
#     + search_data["catchup_ids"]
#     + search_data["highlight_ids"]
#     )
    
#     dates = extract_dates(response)
#     print(f"DEBUG → Dates: {dates}")

#     try:
#         #  Primary validation
#         assert expected_event_id in search_event_ids

#         result = "PASS"
#         error_message = ""

#     except AssertionError:

#         result = "FAIL"

#         #  Intelligent failure classification (ORDER MATTERS)
#         if is_day_stage_pattern(prompt) and dates:
#             error_message = f"Day/Stage misinterpreted as date: {dates}"

#         elif not has_date_intent(prompt) and dates:
#             error_message = f"Unexpected date filter applied: {dates}"

#         elif not search_event_ids:
#             error_message = "No results returned"

#         else:
#             error_message = f"Expected GUID not found. Found IDs: {search_event_ids}"

#     #  Logging
#     if result == "FAIL":
#         with open(file_path, "a") as f:
#             f.write(
#             f"PROMPT: {prompt} | "
#             f"TIME: {response_time}s | "
#             f"RESULT: {result} | "
#             f"REASON: {error_message}\n"
#         )


#     #  Keep pytest failure behavior
#     if result == "FAIL":
#         pytest.fail(error_message)



@pytest.mark.parametrize("data", load_schedule_sport_prompts())
def test_search_with_schedule_sport_prompts(data):
    
    sport_title = data["sport_title"]
    prompt = data["prompt"]
    expected_event_ids = set(data["expected_event_ids"])

    print(f"\nTesting Sport: {sport_title}")
    print(f"Prompt: {prompt}")

    start_time = time.time()
    response = search_api(prompt)
    response_time = round(time.time() - start_time, 2)

    search_data = extract_search_event_ids(response)
    search_event_ids = set(
        search_data["live_ids"]
        + search_data["upcoming_ids"]
        + search_data["catchup_ids"]
        + search_data["highlight_ids"]
    )

    try:
        assert expected_event_ids.issubset(search_event_ids)

        result = "PASS"
        error_message = ""

    except AssertionError:

        result = "FAIL"

        if not search_event_ids:
            error_message = "No results returned"

        else:
            error_message = f"Expected event IDs not found. Found IDs: {search_event_ids}"

    if result == "FAIL":
        with open(file_Path2, "a") as f:
            f.write(
                f"PROMPT: {prompt} | "
                f"TIME: {response_time}s | "
                f"RESULT: {result} | "
                f"REASON: {error_message}\n"
            )

    if result == "FAIL":
        pytest.fail(error_message)