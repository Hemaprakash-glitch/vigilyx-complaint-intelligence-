import json
import time

import requests

BASE_URL = "https://api.fda.gov/device/event.json"


def fetch_page(
    skip: int,
    limit: int = 100,
    search_term: str = None
):
    """
    Fetch a single page of MAUDE records.

    Parameters
    ----------
    skip : int
        Number of records to skip.

    limit : int
        Number of records per request.

    search_term : str, optional
        openFDA search query.

        Examples:
            device.generic_name:"catheter"
            device.device_report_product_code:"OZO"
    """

    params = {
        "skip": skip,
        "limit": limit
    }

    if search_term:
        params["search"] = search_term

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")
        return None

    return response.json()


def fetch_all(
    product_search_term: str = None,
    max_records: int = 500
):
    """
    Fetch MAUDE records.

    Parameters
    ----------
    product_search_term : str, optional
        openFDA search query.

    max_records : int
        Maximum number of records to download.
    """

    all_records = []

    skip = 0

    limit = 100

    while len(all_records) < max_records:

        data = fetch_page(
            skip=skip,
            limit=limit,
            search_term=product_search_term
        )

        if data is None:
            print("Stopping: request failed")
            break

        records = data.get("results", [])

        if not records:
            print("No more records found.")
            break

        all_records.extend(records)

        print(f"Fetched {len(all_records)} records...")

        skip += limit

        # Respect openFDA rate limits
        time.sleep(0.5)

    return all_records[:max_records]


if __name__ == "__main__":

    # Example:
    # device.generic_name:"catheter"
    # device.device_report_product_code:"OZO"

    records = fetch_all(
        product_search_term='device.device_report_product_code:"OZO"',
        max_records=500
    )

    with open(
        "shared/data/maude_sample.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4
        )

    print(
        f"\nSaved {len(records)} records "
        "to shared/data/maude_sample.json"
    )