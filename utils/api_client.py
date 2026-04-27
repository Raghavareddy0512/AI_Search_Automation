import requests
import time

# SEARCH_URL = "https://search.discovery.indazn.com/v1/search"
# SEARCH_URL = "https://search-alb-use1.discovery.dazn-stage.com/v7/search/"
SearchUrl = "https://search-service-prod-apse1-1507421585.ap-southeast-1.elb.amazonaws.com/v1/search/"

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
    response = requests.get(
        SearchUrl,
        params=params ,
        verify= False  #  bypass SSL (for staging/testing only)
    )
    response.raise_for_status()
    return response.json()


