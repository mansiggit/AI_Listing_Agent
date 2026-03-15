import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return gspread.authorize(creds)

def push_to_sheets(data: list, query: str, spreadsheet_url: str = None) -> str:
    client = get_client()
    spreadsheet = client.open_by_url(spreadsheet_url)
    print(f"  → Connected to your Google Sheet...")

    # Create a unique tab name using query + timestamp
    timestamp_short = datetime.now().strftime("%m/%d %H:%M")
    tab_title = f"{query[:35]} ({timestamp_short})"

    try:
        # Try to get existing tab first
        worksheet = spreadsheet.worksheet(tab_title)
        worksheet.clear()
        print(f"  → Cleared existing tab: '{tab_title}'")
    except gspread.exceptions.WorksheetNotFound:
        # Create fresh tab
        worksheet = spreadsheet.add_worksheet(title=tab_title, rows=500, cols=15)
        print(f"  → Created new tab: '{tab_title}'")

    # ── Headers ──────────────────────────────────────────
    headers = [
        "S.No", "Business Name", "Category", "Rating",
        "Total Reviews", "Price Level", "Status", "Address",
        "Phone", "Email", "Website", "Opening Hours", "Open Now", "Scraped At"
    ]

    worksheet.append_row(headers)

    # Bold blue header formatting
    worksheet.format("A1:N1", {
        "backgroundColor": {"red": 0.27, "green": 0.51, "blue": 0.71},
        "textFormat": {
            "bold": True,
            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
            "fontSize": 11
        },
        "horizontalAlignment": "CENTER"
    })

    # ── Data rows ─────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows_to_insert = []

    for i, biz in enumerate(data, 1):

        # Auto status based on rating
        try:
            rating = float(biz.get("rating", 0))
            if rating >= 4.5:   status = "⭐ Top Rated"
            elif rating >= 4.0: status = "👍 Well Rated"
            elif rating >= 3.0: status = "😐 Average"
            else:               status = "👎 Below Average"
        except:
            status = "❓ No Rating"

        # Price level mapping
        price_map = {"1": "$", "2": "$$", "3": "$$$", "4": "$$$$"}
        price_raw = str(biz.get("price", "N/A"))
        price = price_map.get(price_raw, price_raw)

        # Open/Closed status
        open_now = biz.get("open_now")
        open_str = "✅ Open" if open_now is True else "❌ Closed" if open_now is False else "N/A"

        rows_to_insert.append([
            i,
            biz.get("name", ""),
            biz.get("category", ""),
            biz.get("rating", ""),
            biz.get("reviews", ""),
            price,
            status,
            biz.get("address", ""),
            biz.get("phone", "N/A"),
            biz.get("email", "N/A"),
            biz.get("website", ""),
            biz.get("opening_hours", "N/A"),
            open_str,
            timestamp
        ])

    # Batch insert all rows at once (much faster!)
    if rows_to_insert:
        worksheet.append_rows(rows_to_insert)
        print(f"  → Written {len(rows_to_insert)} rows in one batch")

    # Alternating row colors for readability
    for i, row in enumerate(rows_to_insert):
        row_num = i + 2  # offset by 1 for header
        if i % 2 == 0:
            worksheet.format(f"A{row_num}:N{row_num}", {
                "backgroundColor": {"red": 0.93, "green": 0.96, "blue": 1.0}
            })

    # Auto-resize all columns
    requests_body = {
        "requests": [{
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": worksheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 14
                }
            }
        }]
    }
    spreadsheet.batch_update(requests_body)
    print(f"  → Columns auto-resized ✅")

    # Freeze header row so it stays visible when scrolling
    worksheet.freeze(rows=1)
    print(f"  → Header row frozen ✅")

    return spreadsheet.url