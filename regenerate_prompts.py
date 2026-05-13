#!/usr/bin/env python3
"""
Standalone script to regenerate testdata/generated_sport_prompts.json
"""

import json
import os
from utils.schedule import fetch_full_schedule
from utils.generator import generate_sport_prompts_with_expected

def main():
    print("Fetching full schedule...")
    tiles = fetch_full_schedule(days_back=2, days_forward=2)

    print("Generating sport prompts with expected IDs...")
    prompts_data = generate_sport_prompts_with_expected(tiles)

    os.makedirs("testdata", exist_ok=True)
    with open("testdata/generated_sport_prompts.json", "w") as f:
        json.dump({"prompts": prompts_data}, f, indent=4)

    print(f"Saved {len(prompts_data)} prompts to testdata/generated_sport_prompts.json")

if __name__ == "__main__":
    main()