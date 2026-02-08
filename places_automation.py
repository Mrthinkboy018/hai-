#!/usr/bin/env python3
"""Google Places API automation for scrap shop details and website generation."""

import argparse
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests


TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


@dataclass
class PlaceRecord:
    name: str
    address: str
    phone: str
    website: str
    rating: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    place_id: str

    def to_row(self) -> Dict[str, object]:
        return {
            "Name": self.name,
            "Address": self.address,
            "Phone": self.phone,
            "Website": self.website,
            "Rating": self.rating,
            "Latitude": self.latitude,
            "Longitude": self.longitude,
            "Place ID": self.place_id,
        }


def sanitize_filename(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower())
    return normalized.strip("_") or "location"


def sanitize_folder_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    return normalized.strip("_") or "shop"


def digits_only(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def fetch_text_search_results(api_key: str, query: str, max_pages: int = 3) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    params = {"query": query, "key": api_key}

    for _ in range(max_pages):
        response = requests.get(TEXT_SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        results.extend(payload.get("results", []))

        next_token = payload.get("next_page_token")
        if not next_token:
            break

        params = {"pagetoken": next_token, "key": api_key}
        time.sleep(2)

    return results


def fetch_place_details(api_key: str, place_id: str) -> Dict[str, object]:
    fields = [
        "name",
        "formatted_address",
        "formatted_phone_number",
        "website",
        "rating",
        "geometry/location",
        "place_id",
    ]
    params = {
        "place_id": place_id,
        "fields": ",".join(fields),
        "key": api_key,
    }
    response = requests.get(DETAILS_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload.get("result", {})


def build_place_record(details: Dict[str, object]) -> PlaceRecord:
    geometry = details.get("geometry", {})
    location = geometry.get("location", {}) if isinstance(geometry, dict) else {}

    return PlaceRecord(
        name=details.get("name", "Unknown"),
        address=details.get("formatted_address", "Not available"),
        phone=details.get("formatted_phone_number", "Not available"),
        website=details.get("website", "Not available"),
        rating=details.get("rating"),
        latitude=location.get("lat"),
        longitude=location.get("lng"),
        place_id=details.get("place_id", ""),
    )


def collect_places(api_key: str, keyword: str, location: str, max_pages: int) -> List[PlaceRecord]:
    query = f"{keyword} in {location}"
    search_results = fetch_text_search_results(api_key, query, max_pages=max_pages)

    records: List[PlaceRecord] = []
    seen_place_ids = set()

    for item in search_results:
        place_id = item.get("place_id")
        if not place_id or place_id in seen_place_ids:
            continue

        details = fetch_place_details(api_key, place_id)
        record = build_place_record(details)
        records.append(record)
        seen_place_ids.add(place_id)

    return records


def write_excel(records: Iterable[PlaceRecord], location: str, output_dir: str) -> str:
    data = [record.to_row() for record in records]
    df = pd.DataFrame(data, columns=[
        "Name",
        "Address",
        "Phone",
        "Website",
        "Rating",
        "Latitude",
        "Longitude",
        "Place ID",
    ])

    os.makedirs(output_dir, exist_ok=True)
    filename = f"scrap_shops_{sanitize_filename(location)}.xlsx"
    path = os.path.join(output_dir, filename)
    df.to_excel(path, index=False, engine="openpyxl")
    return path


def build_html_template(record: PlaceRecord) -> str:
    phone_display = record.phone if record.phone != "Not available" else "Phone not available"
    phone_digits = digits_only(record.phone)
    whatsapp_link = f"https://wa.me/{phone_digits}" if phone_digits else "#"
    whatsapp_class = "" if phone_digits else "disabled"

    map_src = ""
    if record.latitude is not None and record.longitude is not None:
        map_src = (
            "https://www.google.com/maps?q="
            f"{record.latitude},{record.longitude}&z=15&output=embed"
        )

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{record.name}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background: #f5f5f5;
      color: #222;
    }}
    header {{
      background: #1b5e20;
      color: #fff;
      padding: 20px;
      text-align: center;
    }}
    main {{
      max-width: 960px;
      margin: 20px auto;
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    .info {{
      display: grid;
      gap: 16px;
    }}
    .cta {{
      display: inline-block;
      margin-top: 10px;
      padding: 10px 16px;
      background: #25d366;
      color: #fff;
      text-decoration: none;
      border-radius: 4px;
    }}
    .cta.disabled {{
      background: #ccc;
      pointer-events: none;
    }}
    iframe {{
      width: 100%;
      height: 320px;
      border: 0;
      border-radius: 6px;
    }}
    form {{
      display: grid;
      gap: 12px;
    }}
    input, textarea {{
      width: 100%;
      padding: 10px;
      border-radius: 4px;
      border: 1px solid #ccc;
    }}
    button {{
      background: #1b5e20;
      color: #fff;
      border: none;
      padding: 10px;
      border-radius: 4px;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{record.name}</h1>
  </header>
  <main>
    <section class=\"info\">
      <div>
        <h2>Address</h2>
        <p>{record.address}</p>
      </div>
      <div>
        <h2>Phone</h2>
        <p>{phone_display}</p>
        <a class=\"cta {whatsapp_class}\" href=\"{whatsapp_link}\" target=\"_blank\" rel=\"noopener\">WhatsApp</a>
      </div>
    </section>
    <section>
      <h2>Location</h2>
      {'<iframe src="' + map_src + '"></iframe>' if map_src else '<p>Map not available.</p>'}
    </section>
    <section>
      <h2>Contact Us</h2>
      <form>
        <input type=\"text\" name=\"name\" placeholder=\"Your Name\" required />
        <input type=\"email\" name=\"email\" placeholder=\"Email Address\" required />
        <textarea name=\"message\" rows=\"4\" placeholder=\"How can we help?\" required></textarea>
        <button type=\"submit\">Send Message</button>
      </form>
    </section>
  </main>
</body>
</html>"""


def generate_websites(records: Iterable[PlaceRecord], output_dir: str) -> List[str]:
    paths: List[str] = []
    for record in records:
        folder_name = sanitize_folder_name(record.name)
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "index.html")
        with open(file_path, "w", encoding="utf-8") as html_file:
            html_file.write(build_html_template(record))
        paths.append(file_path)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect scrap shop details from Google Places API.")
    parser.add_argument("--keyword", required=True, help="Business keyword, e.g. 'scrap shop'.")
    parser.add_argument("--location", required=True, help="City/district/state to search.")
    parser.add_argument("--api-key", default=os.getenv("GOOGLE_PLACES_API_KEY"), help="Google Places API key.")
    parser.add_argument("--max-pages", type=int, default=3, help="Number of result pages to request.")
    parser.add_argument("--output-dir", default="output", help="Directory for Excel output.")
    parser.add_argument("--website-dir", default="websites", help="Directory for generated websites.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.api_key:
        raise SystemExit("Google Places API key required via --api-key or GOOGLE_PLACES_API_KEY.")

    records = collect_places(args.api_key, args.keyword, args.location, args.max_pages)
    if not records:
        raise SystemExit("No results found. Try adjusting keyword or location.")

    excel_path = write_excel(records, args.location, args.output_dir)
    generate_websites(records, args.website_dir)

    print(f"Saved {len(records)} records to {excel_path}")
    print(f"Websites created in {args.website_dir}/")


if __name__ == "__main__":
    main()
