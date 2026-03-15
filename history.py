import json
import os
from datetime import datetime

HISTORY_FILE = "search_history.json"

def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_to_history(query: str, result_count: int, sheet_url: str):
    history = load_history()
    history.append({
        "query":        query,
        "results":      result_count,
        "sheet_url":    sheet_url,
        "searched_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def print_history():
    history = load_history()
    if not history:
        print("\n  📭 No search history yet.\n")
        return

    print(f"\n  📜 Search History ({len(history)} searches)")
    print("  " + "─"*55)
    for i, h in enumerate(reversed(history[-10:]), 1):
        print(f"  {i:>2}. [{h['searched_at']}]")
        print(f"      🔎 {h['query']}")
        print(f"      📊 {h['results']} listings found")
        print()