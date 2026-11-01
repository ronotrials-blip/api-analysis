
"""
Day 1 - API Data Analysis Using Python Structures
"""

# importing the required libraries
import json
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
OUT_DIR = Path("output")


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        resp = requests.get(url, timeout=10) # 10s stops the script hanging if the server doesn't respond.
    except requests.RequestException as e:
        print(f"Network error: could not reach {url} ({e})")
        return []
    if resp.status_code != 200: # means success
        print(f"Request failed: {url} returned status {resp.status_code}")
        return []
    return resp.json() # convert response text into dictionaries.


def explore(record, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth.

    Recursive: dicts are walked key by key, and lists are sampled at their first item.
    """
    if isinstance(record, dict):
        for key, value in record.items():
            print("  " * indent + f"{key}: {type(value).__name__}") # Print key and its type
            explore(value, indent + 1)
    elif isinstance(record, list) and record: # only explore non-empty lists
        print("  " * indent + f"[list of {len(record)}, items: {type(record[0]).__name__}]")
        explore(record[0], indent + 1)


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
    for c in customers:
        addr = c["address"]
        geo = addr["geo"]
        email = c["email"]
        rows.append({
            "customer_id": c["id"],
            "name": c["name"],
            "username": c["username"],
            "email": email,
            "email_domain": email.rsplit(".", 1)[-1],  # top-level domain, e.g. 'biz'
            "phone": c["phone"],
            "city": addr["city"],
            "zipcode": addr["zipcode"],
            "latitude": float(geo["lat"]),
            "longitude": float(geo["lng"]),
            "company": c["company"]["name"],
            "website": c["website"],
        })
    return rows


#Use sets to find unique cities
def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["city"] for c in customers}


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city with a plain loop (no Counter, no pandas).
    Sorted by count descending, then city name."""
    counts: dict[str, int] = {}
    for c in customers:
        counts[c["city"]] = counts.get(c["city"], 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain with a dict comprehension."""
    tlds = {c["email_domain"] for c in customers}
    counts = {t: sum(1 for c in customers if c["email_domain"] == t) for t in tlds}
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def plot_distribution(counts: dict[str, int], path: Path,
                      title: str = "Customers by city", xlabel: str = "City") -> None:
    """Save a labelled bar chart of the distribution to path."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(list(counts.keys()), list(counts.values()), color="#2E86AB")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Customers")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    customers = get_customers()
    if not customers:
        return

    print("--- Structure of one record ---")
    explore(customers[0])

    rows = extract_attributes(customers)
    cities = unique_cities(rows)
    city = city_counts(rows)
    domains = email_domain_counts(rows)

    top_city, top_n = next(iter(city.items()))
    print("\n--- Findings ---")
    print(f"Customers retrieved : {len(customers)}")
    print(f"Unique cities       : {len(cities)}")
    print(f"Most common city    : {top_city} ({top_n})")
    print(f"Email domains       : {domains}")

    df = to_dataframe(rows)
    print(f"\nDataFrame shape: {df.shape}")
    print(df.dtypes)
    pandas_counts = df["city"].value_counts()
    agrees = all(pandas_counts[c] == n for c, n in city.items())
    print(f"Pandas agrees with city counts: {agrees}")

    df.to_csv(OUT_DIR / "customers.csv", index=False)
    pd.DataFrame(
        [{"city": c, "customer_count": n} for c, n in city.items()]
    ).to_csv(OUT_DIR / "city_counts.csv", index=False)

    chart = OUT_DIR / "customer_distribution.png"
    plot_distribution(city, chart)
    plot_distribution(domains, OUT_DIR / "email_domain_distribution.png",
                      title="Customers by email top-level domain",
                      xlabel="Email top-level domain")
    print(f"Chart saved to      : {chart}")


if __name__ == "__main__":
    main()
    
