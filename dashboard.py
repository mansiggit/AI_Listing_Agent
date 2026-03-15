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

def update_dashboard(spreadsheet_url: str, query: str, businesses: list):
    """Create or update a Dashboard tab with summary stats"""
    client = get_client()
    spreadsheet = client.open_by_url(spreadsheet_url)

    # Get or create Dashboard tab
    try:
        dash = spreadsheet.worksheet("📊 Dashboard")
        dash.clear()
    except gspread.exceptions.WorksheetNotFound:
        dash = spreadsheet.add_worksheet(title="📊 Dashboard", rows=200, cols=10)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Calculate Stats ───────────────────────────────────
    total        = len(businesses)
    has_website  = sum(1 for b in businesses if b.get("website",  "N/A") != "N/A")
    has_phone    = sum(1 for b in businesses if b.get("phone",    "N/A") != "N/A")
    has_email    = sum(1 for b in businesses if b.get("email",    "N/A") != "N/A")
    top_rated    = sum(1 for b in businesses if float(b.get("rating", 0) or 0) >= 4.5)

    ratings = [
        float(b.get("rating", 0))
        for b in businesses
        if b.get("rating") and b.get("rating") != "N/A"
    ]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else "N/A"

    # Top 5 by rating
    sorted_biz = sorted(
        [b for b in businesses if b.get("rating") and b.get("rating") != "N/A"],
        key=lambda x: float(x.get("rating", 0)),
        reverse=True
    )[:5]

    # ── Write Dashboard ────────────────────────────────────
    rows = [
        ["📊 AI BUSINESS LISTING AGENT — DASHBOARD", ""],
        ["Last Updated", now],
        ["", ""],
        ["🔎 LATEST SEARCH SUMMARY", ""],
        ["Query",         query],
        ["Total Listings", total],
        ["Avg Rating",    avg_rating],
        ["⭐ Top Rated (4.5+)", top_rated],
        ["", ""],
        ["📬 CONTACT INFO COVERAGE", ""],
        ["Has Website",  f"{has_website}/{total} ({round(has_website/total*100)}%)"],
        ["Has Phone",    f"{has_phone}/{total}   ({round(has_phone/total*100)}%)"],
        ["Has Email",    f"{has_email}/{total}   ({round(has_email/total*100)}%)"],
        ["", ""],
        ["🏆 TOP 5 BUSINESSES", "Rating"],
    ]

    for b in sorted_biz:
        rows.append([b.get("name", "N/A"), b.get("rating", "N/A")])

    dash.update("A1", rows)

    # ── Formatting ─────────────────────────────────────────
    # Title row
    dash.format("A1:B1", {
        "backgroundColor": {"red": 0.17, "green": 0.24, "blue": 0.47},
        "textFormat": {
            "bold": True,
            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
            "fontSize": 13
        }
    })

    # Section headers
    for row_num in [4, 10, 15]:
        dash.format(f"A{row_num}:B{row_num}", {
            "backgroundColor": {"red": 0.27, "green": 0.51, "blue": 0.71},
            "textFormat": {
                "bold": True,
                "foregroundColor": {"red": 1, "green": 1, "blue": 1}
            }
        })

    # Top 5 rows
    for i in range(len(sorted_biz)):
        row_num = 16 + i
        if i % 2 == 0:
            dash.format(f"A{row_num}:B{row_num}", {
                "backgroundColor": {"red": 0.93, "green": 0.96, "blue": 1.0}
            })

    # Auto-resize columns
    spreadsheet.batch_update({"requests": [{
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": dash.id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 2
            }
        }
    }]})

    # Move Dashboard to first tab
    spreadsheet.batch_update({"requests": [{
        "updateSheetProperties": {
            "properties": {
                "sheetId": dash.id,
                "index": 0
            },
            "fields": "index"
        }
    }]})

    print(f"  → Dashboard updated ✅")