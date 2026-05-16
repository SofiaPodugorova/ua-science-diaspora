import requests, json, time
from pathlib import Path

BASE = "https://api.openalex.org/works"
PARAMS = {
    "filter": "authorships.institutions.country_code:ua,publication_year:2018-2024,concepts.id:C162324750",
    "per-page": 200,
    "mailto": "sofiapodugo@gmail.com",  
}
MAX_PAGES = 25  # ~5000 works total

def fetch_all(out_dir="data/raw"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    cursor, page = "*", 0
    while cursor and page < MAX_PAGES:
        r = requests.get(BASE, params={**PARAMS, "cursor": cursor}, timeout=30)
        r.raise_for_status()
        data = r.json()
        Path(f"{out_dir}/page_{page:05d}.json").write_text(
            json.dumps(data["results"]), encoding="utf-8"
        )
        cursor = data["meta"].get("next_cursor")
        page += 1
        print(f"page {page}/{MAX_PAGES}: +{len(data['results'])} works")
        time.sleep(0.1)
    print(f"done, {page} pages saved")

if __name__ == "__main__":
    fetch_all()