import requests
import time

SEARCH_URL = "https://search.discovery.indazn.com/v1/search"
# SEARCH_URL = "https://search-alb-use1.discovery.dazn-stage.com/v7/search/"


def search_api(prompt):

    params = {
        "langCode": "en",
        "openBrowse": "true",
        "metaInfo": "true",
        "llmEnabled": "true",
        "brand": "dazn",
        "country": "ca",
        "searchTerm": prompt,
        "version": "v7",
        "ragEnabled": "true"
    }
    start_time = time.time()
    response = requests.get(
        SEARCH_URL,
        params=params
    )
    end_time = time.time()

    response.raise_for_status()
    response_time = end_time - start_time
    print(f"Search API response time: {response_time:.2f} seconds")
    # print(f"API Response : {response.json()}")
    return response.json()
