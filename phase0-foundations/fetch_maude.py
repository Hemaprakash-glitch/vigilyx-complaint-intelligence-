import requests
import json
import time

BASE_URL = "https://api.fda.gov/device/event.json"


def fetch_page(skip: int, limit: int = 100):
    params = {
        "skip": skip,
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")
        return None

    return response.json()


def fetch_all(max_records: int = 500):
    all_records = []
    skip = 0
    limit = 100

    while len(all_records) < max_records:
        data = fetch_page(skip, limit)

        if data is None:
            print("Stopping: request failed")
            break

        records = data["results"]

        if not records:
            break

        all_records.extend(records)

        skip += limit

        time.sleep(0.5)

    return all_records[:max_records]


if __name__ == "__main__":
    records = fetch_all()

    # Write records to JSON file
    with open("shared/data/maude_sample.json", "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    print(f"Saved {len(records)} records to shared/data/maude_sample.json")