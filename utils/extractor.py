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

def validate_dates(response):

    dates = []

        # Try all possible LLM blocks (DAZN varies across regions)
    llm = (
         response.get("llmResponseObj")
            or response.get("llmResponse")
         or response.get("llmResult")
                                or None
        )
    if not llm:
            return None

    result = llm.get("result", {})
    start_date = result.get("startDate")
    end_date = result.get("endDate")

    if start_date:
        dates.append(start_date)
    if end_date:
       dates.append(end_date)
    return dates    


def extract_search_event_ids(response):

    event_ids = []
    results = response.get("Results", [])
    for category in results:
        if category.get("Id") == "searchCategory_events":
            for tile in category.get("Tiles", []):
                event_id = tile.get("Id") or tile.get("AssetId")
                if event_id:
                    event_ids.append(event_id)
    return event_ids



