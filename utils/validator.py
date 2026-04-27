
import re

def validate_list(expected, actual, field_name):

    missing = []

    for value in expected:
        if value not in actual:
            missing.append(value)

    if missing:
        raise AssertionError(
            f"\n{field_name} Validation Failed\n"
            f"Expected : {expected}\n"
            f"Actual   : {actual}\n"
            f"Missing  : {missing}"
        )
    


def has_date_intent(prompt: str):
    return bool(re.search(
        r"\b(today|tomorrow|yesterday|date|week|month|year|"
        r"\d{1,2}[-/]\d{1,2}|"
        r"\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|"
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2})\b",
        prompt.lower()
    ))

def is_day_stage_pattern(prompt: str):
    return bool(re.search(
        r"\b(day|stage|round)\s*[-:]?\s*\d+\b",
        prompt.lower()
    ))


def validate_event_ids(expected_guid, actual_guids):

    if expected_guid not in actual_guids:
        raise AssertionError(
            f"\nGUID Validation Failed\n"
            f"Expected GUID: {expected_guid}\n"
            f"Actual GUIDs: {actual_guids}\n"
        )
    
    