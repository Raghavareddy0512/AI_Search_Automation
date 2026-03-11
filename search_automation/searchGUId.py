import requests
import json

# url = "https://search.discovery.indazn.com/v1/search?langCode=en&openBrowse=true&metaInfo=true&llmEnabled=true&brand=dazn&country=ca&searchTerm=soccer&version=v7&ragEnabled=true"

# response = requests.get(url)
# data = response.json()
# print(json.dumps(data, indent=4))

def search_api(prompt):
    url = "https://search.discovery.indazn.com/v1/search"
    params = {
        "langCode": "en",
        "openBrowse": "true",
        "metaInfo": "true",
        "llmEnabled": "true",
        "brand": "dazn",
        "country": "ca",
        "searchTerm": prompt,
        "version": "v7",
        "ragEnabled": "false"
    }
    return requests.get(url, params=params).json()

data = search_api("serie a highlights")
# print(json.dumps(data, indent=4))


# 1️⃣ Your expected GUIDs
expected_guids = {
    "scf9p4y91yjvqvg5jndxzhxj",
    "1r097lpxe0xn03ihb7wi98kao",
    "6tuibxq39fdryu8ou06wcm0q3",
    "af91jdcs6x0bqkmdb78rokod2",
    "bi1fxjrncd0ram0oi7ja1jyuo",
    "btcy9nra9ak4m22ovr2ia6m5v",
    # add all valid GUIDs here…
}

# 2️⃣ recursively extract all fields named "guid" or "Id"
def extract_guids(data, collected=None):
    if collected is None:
        collected = set()

    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() == "guid" or key.lower() == "id":
                collected.add(value)
            extract_guids(value, collected)

    elif isinstance(data, list):
        for item in data:
            extract_guids(item, collected)

    return collected



# 3️⃣ Call API
data = search_api("serie a highlights")

# 4️⃣ Extract returned GUIDs
returned_guids = extract_guids(data)

print("\nReturned GUID count:", len(returned_guids))

# 5️⃣ Compare against expected list
missing = returned_guids - expected_guids
extra = expected_guids - returned_guids

print("\n--- GUID VALIDATION REPORT ---\n")

# Assert no unexpected GUIDs found in response
assert not missing, f"Unexpected GUIDs found in API response: {missing}"

# Assert no expected GUIDs are missing from response
assert extra, f"Expected GUIDs missing in API response: {extra}"

print("All API GUIDs match the expected list!")