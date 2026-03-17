import json
from urllib import response
import pytest

from utils.api_client import search_api
from utils.extractor import extract_article_types, extract_guids, extract_strategy
from utils.extractor import extract_category
from utils.schedule import schedule_api, extract_schedule_ids, fetch_full_schedule
from utils.extractor import extract_search_event_ids
from utils.validator import validate_list

@pytest.fixture(scope="session")
def schedule_ids():

    print("\nFetching EPG Schedule...")

    schedule_ids = set(fetch_full_schedule())

    print(f"Total Schedule Events: {len(schedule_ids)}")

    return schedule_ids


def load_tests():
    with open("testdata/date_range.json") as f:
        return json.load(f)["tests"]


@pytest.mark.parametrize("test_data", load_tests())
def test_search_validation(test_data, schedule_ids):

    print(f"\nRunning Test: {test_data['test_name']}")
    print(f"Prompt: {test_data['prompt']}")

    response = search_api(test_data["prompt"])
    # print("\nFull API Response:")
    # print(json.dumps(response, indent=2))

    # ---------- Strategy ----------
    # actual_strategy = extract_strategy(response)
    # print("Actual Strategy:", actual_strategy)
    # assert test_data["expected_strategy"] in actual_strategy,\
    # f"Strategy mismatch | Actual: {actual_strategy}"
    

    # ---------- Category ----------
    # actual_category = extract_category(response)
    # print("Actual Category:", actual_category)
    # assert actual_category == test_data["expected_category"], \
    #     f"Category mismatch | Expected: {test_data['expected_category']} Actual: {actual_category}"

    # # ----------  Search IDs----------

    search_event_ids = set(extract_search_event_ids(response))

    print("Search Event IDs:", search_event_ids)
    print("Total Search Events:", len(search_event_ids))

    matched = search_event_ids & schedule_ids
    missing = search_event_ids - schedule_ids
    print("Matched Schedule Events:", matched)
    print("Events not in schedule:", missing)

    assert matched, "No search events matched with schedule"


    # ---------- GUID ----------
    # actual_guids = extract_guids(response)
    # print("Actual GUIDs \n:", actual_guids)
    # validate_list(
    #     test_data["expect_guid"],
    #     actual_guids,
    #     "GUID"
    # )

    # # ---------- Article Type ----------
    # if "expected_article_type" in test_data:

    #     actual_articles = extract_article_types(response)
    #     print("Actual Article Types:", actual_articles)
    #     validate_list(
    #         test_data["expected_article_type"],
    #         actual_articles,
    #         "Article Type"
    #     )