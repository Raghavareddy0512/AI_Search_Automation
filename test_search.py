import pytest
import json
import time

from utils.api_client import search_api
from utils.extractor import extract_search_event_ids
from utils.schedule import (
    extract_schedule_two_days,
)
from utils.generator import generate_title_prompts
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

    events = extract_schedule_two_days()

    for event in events:
        title = event["title"]
        guid = event["guid"]

        prompts = generate_title_prompts(title)

        for prompt in prompts:
            record = {
                "title": title,
                "prompt": prompt,
                "expected_guid": guid
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


# ------------------ MAIN TEST (DYNAMIC + STRONG VALIDATION ) ------------------

# @pytest.mark.parametrize("data", load_schedule_title_prompts())
# def test_search_with_schedule_title_prompts(data):

#     print(f"\nTesting Title: {data['title']}")
#     print(f"Prompt: {data['prompt']}")
#     start_time = time.time()
#     response = search_api(data["prompt"])
#     response_time = round(time.time() - start_time, 2)
#     search_event_ids = set(extract_search_event_ids(response))

#     # print("Search Event IDs:", search_event_ids)
#     # print("Total Search Events:", len(search_event_ids))

#     #  STRONG VALIDATION (exact GUID match)
#     assert data["expected_guid"] in search_event_ids, \
#         f"FAILED | Title: {data['title']} | Prompt: {data['prompt']} | Time: {response_time}s"

    
# ------------------ MAIN TEST (DYNAMIC + STRONG VALIDATION ) ------------------
file_path = "testdata/test_results.txt"


@pytest.mark.parametrize("data", load_schedule_title_prompts())
def test_search_with_schedule_title_prompts(data):

    title = data["title"]
    prompt = data["prompt"]
    expected_guid = data["expected_guid"]

    print(f"\nTesting Title: {title}")
    print(f"Prompt: {prompt}")

    start_time = time.time()
    response = search_api(prompt)
    response_time = round(time.time() - start_time, 2)

    search_event_ids = set(extract_search_event_ids(response))

    try:
        #  actual validation
        assert expected_guid in search_event_ids

        result = "PASS"
        error_message = ""

    except AssertionError as e:
        result = "FAIL"
        error_message = str(e)

    #  ALWAYS log result (PASS or FAIL)
    with open(file_path, "a") as f:
        f.write(
            # f"TITLE: {title} | "
            f"PROMPT: {prompt} | "
            f"TIME: {response_time}s | "
            f"RESULT: {result}\n"
            # f"{error_message}\n"
        )
    #  re-raise failure so pytest still marks it FAILED
    if result == "FAIL":
        pytest.fail(error_message)