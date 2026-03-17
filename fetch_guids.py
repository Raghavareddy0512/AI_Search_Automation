import json
from utils.api_client import search_api
from utils.extractor import extract_guids

def fetch_and_print_guids():
    
    with open("testdata/competition.json") as f:
        tests = json.load(f)["tests"]
    
    results = []
    
    for test in tests:
        test_name = test["test_name"]
        prompt = test["prompt"]
        
        print(f"\n--- Test {test_name}: {prompt} ---")
        
        try:
            response = search_api(prompt)
            guids = extract_guids(response)
            
            print(f"GUIDs: {guids}")
            
            results.append({
                "test_name": test_name,
                "prompt": prompt,
                "guids": guids
            })
            
        except Exception as e:
            print(f"Error fetching GUIDs for '{prompt}': {str(e)}")
            results.append({
                "test_name": test_name,
                "prompt": prompt,
                "guids": [],
                "error": str(e)
            })
    
    # Save results to a file
    with open("guid_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to guid_results.json")
    print(f"Total tests processed: {len(results)}")

if __name__ == "__main__":
    fetch_and_print_guids()
