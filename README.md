
# Day 1: API Data Analysis Using Python Structures

Analysis of customer data from the JSONPlaceholder users API, framed as the first step in planning regional campaigns for Pesa Pulse.

## Project structure

api-analysis/
├── analysis.py
├── requirements.txt
├── README.md
└── output/
├── customers.csv
├── city_counts.csv
├── customer_distribution.png
└── email_domain_distribution.png


## How to run

Requires Python 3.11 or later.

```bash
git clone https://github.com/ronotrials-blip/api-analysis.git
cd api-analysis
python3 -m pip install -r requirements.txt
python3 analysis.py
```

Run the script from the project root, since it writes to `output/` relative to the current folder. The script needs an internet connection.

## Approach

1. Fetch. `get_customers` requests the user list with a 10-second timeout. A network error or a non-200 status prints a message and returns an empty list, so the script stops cleanly instead of showing a traceback.
2. Explore. `explore` walks one record recursively and prints each key with its type, indented by depth. This shows that `address` contains `geo`, and that `lat` and `lng` are stored as strings.
3. Flatten. `extract_attributes` pulls the 12 required attributes out of the nested dictionaries into one flat dictionary per customer. The email top-level domain is taken from the last dot in the address, and latitude and longitude are converted to floats.
4. Count without libraries. `unique_cities` uses a set comprehension. `city_counts` uses a loop with `dict.get`, and `email_domain_counts` uses a dict comprehension. Both count results are sorted by count, highest first, then alphabetically.
5. Check with pandas. The data is loaded into a DataFrame, and `value_counts()` is compared with the hand-written city counts. The script prints `True` only if they all match.
6. Export and chart. The DataFrame is saved to `customers.csv`, and the city counts to `city_counts.csv`, both without the index. Two bar charts are saved: one for cities and one for email top-level domains.

## Findings

Results from the run on 10 customers:

1. Every customer is in a different city. There are 10 unique cities for 10 customers, so every city has a count of 1. The most common city is therefore a tie, and the script lists the alphabetically first one (Aliyaview). The city chart is flat and can't show where customers cluster, so it isn't useful for choosing regional campaigns.
2. Email top-level domains show some grouping. `.biz` accounts for 3 customers, and `.ca`, `.info`, `.io`, `.me`, `.net`, `.org`, and `.tv` each account for 1. The domain chart is the more useful of the two for a slide, though the sample is too small to draw firm conclusions.
3. Coordinates come back as text. The API returns latitude and longitude as strings. They have to be converted to numbers before they can be used for mapping or distance calculations.

## Assumptions

- The data is JSONPlaceholder mock data, not real Pesa Pulse customers. The Pesa Pulse framing is only the scenario for the analysis.
- Addresses, coordinates, and company details are fictional.
- Email top-level domain is the part after the last dot, so `.co.ke` would be reported as `ke`. This doesn't affect the current data, which has no such addresses.
- The sample is 10 customers, so the counts describe this dataset only and not the wider market.
