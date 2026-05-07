ASSET_TYPES = {
        "LIVE": "19bajo019znum1tkhzn0qz6iy4",
        "UPCOMING": "1f2vso6mwht2x1x9hi3euru0fb",
        "CATCHUP": "1k7t7oc0q1omt19gij7s3hc676",
        "HIGHLIGHT": "1dpp4008gvoq81nbxq0iu9x2jv"
    }



def extract_strategy(response):
    return response.get(
        "strategyResolver", {}
    ).get("name", "")


def extract_category(response):

    llm = (
        response.get("llmResponseObj")
    )
    if not llm:
        return None

    resultObj = llm.get("result", {})
    result = resultObj.get("llmJson", {})

    if result.get("sports"):
        return "sports"
    if result.get("competitions"):
        return "competitions"
    if result.get("teams"):
        return "contestants"
    if result.get("players"):
        return "contestants"
    if result.get("contestants"):
        return "contestants"

    return None


def extract_guids(response):

    guid_list = []

    # 1. get LLM block
    llm = response.get("llmResponseObj")
    if not llm:
        return guid_list

    # 2. get result block
    result = llm.get("result", {})

    # 3. get linearMflSearchTerm list
    terms = result.get("linearMflSearchTerm", [])

    # 4. loop through list
    for item in terms:
        # item is a dict like {"sport": [ ... ]}
        for key, value in item.items():
            # value is a list of entities
            if isinstance(value, list):
                for entity in value:
                    guid = entity.get("guid")
                    if guid:
                        guid_list.append(guid)

    return guid_list


def extract_article_types(response):

    article_types = []

    # Try all possible LLM blocks (DAZN varies across regions)
    llm = (
        response.get("llmResponseObj")
        or response.get("llmResponse")
        or response.get("llmResult")
        or None
    )

    if not llm:
        return article_types

    result = llm.get("result", {})

    # Extract articleType
    article_type = result.get("articleType")

    if article_type:
        article_types.append(article_type)

    return article_types


def classify_asset_type(article_type):
    """
    Classify assetType into categories based on article_type value.
    Update the mapping as needed based on actual data.
    """
    mapping = {
        "1k7t7oc0q1omt19gij7s3hc676": "upcoming",
        "1dpp4008gvoq81nbxq0iu9x2jv": "catchup",
        # Add more mappings for highlights or other types
    }
    return mapping.get(article_type, "highlights")


def extract_dates(response):
    dates = []

    llm = response.get("llmResponseObj")
    if not llm:
        return []  #  always return list

    result = llm.get("result", {})
    if not result:
        return []

    start_date = result.get("startDate")
    end_date = result.get("endDate")

    if start_date:
        dates.append(start_date)
    if end_date:
        dates.append(end_date)
    return dates


def extract_search_event_ids(response):

    ASSET_TYPES = {
        "LIVE": "19bajo019znum1tkhzn0qz6iy4",
        "UPCOMING": "1f2vso6mwht2x1x9hi3euru0fb",
        "CATCHUP": "1k7t7oc0q1omt19gij7s3hc676",
        "HIGHLIGHT": "1dpp4008gvoq81nbxq0iu9x2jv"
    }

    event_ids = set()
    article_ids = set()
    live = set()
    upcoming = set()
    catchup = set()
    highlight = set()

    results = response.get("Results", [])

    for category in results:
        if category.get("Id") != "searchCategory_events":
            continue

        for tile in category.get("Tiles", []):
            article_id = tile.get("AssetId") or tile.get("assetId")
            event_id = tile.get("EventId") or tile.get("eventId")
            asset_type = tile.get("AssetTypeId") or tile.get("assetTypeId")

            if not article_id or not asset_type:
                continue

            event_ids.add(event_id)
            article_ids.add(article_id)

            if asset_type == ASSET_TYPES["LIVE"]:
                live.add(article_id)

            elif asset_type == ASSET_TYPES["UPCOMING"]:
                upcoming.add(article_id)

            elif asset_type == ASSET_TYPES["CATCHUP"]:
                catchup.add(article_id)

            elif asset_type == ASSET_TYPES["HIGHLIGHT"]:
                highlight.add(article_id)

    return {
        "article_ids": list(article_ids),
        "event_ids": list(event_ids),
        "live_ids": list(live),
        "upcoming_ids": list(upcoming),
        "catchup_ids": list(catchup),
        "highlight_ids": list(highlight),
    }