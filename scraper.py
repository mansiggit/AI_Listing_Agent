import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_businesses(query: str) -> list:
    print(f"  → Hitting Serper API for: '{query}'")

    url = "https://google.serper.dev/maps"
    payload = {"q": query, "num": 20}
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"  ❌ Serper API error: {e}")
        return []

    places = data.get("places", [])

    if not places:
        print(f"  ⚠️  No results found. Try rephrasing your query.")
        return []

    results = []
    for place in places:

        # Format opening hours from dict → readable string
        opening_hours_raw = place.get("openingHours", {})
        if isinstance(opening_hours_raw, dict) and opening_hours_raw:
            hours_str = " | ".join(
                f"{day}: {time}" for day, time in opening_hours_raw.items()
            )
        else:
            hours_str = "N/A"

        results.append({
            "name":          place.get("title")       or "N/A",
            "category":      place.get("type")        or "N/A",
            "rating":        place.get("rating")      or "N/A",
            "reviews":       place.get("ratingCount") or "N/A",
            "price":         place.get("priceLevel")  or "N/A",
            "address":       place.get("address")     or "N/A",
            "phone":         "N/A",  # extracted from website later
            "email":         "N/A",  # extracted from website later
            "website":       place.get("website")     or "N/A",
            "opening_hours": hours_str,
            "open_now":      place.get("openNow")     or None,
            "thumbnail":     place.get("thumbnailUrl")or "N/A",
        })

    print(f"  ✅ Found {len(results)} listings")
    return results