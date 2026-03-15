import os
from dotenv import load_dotenv
from agent import run_agent
from batch import run_batch
from history import print_history

load_dotenv()

def banner():
    print("\n" + "="*55)
    print("   🏢  AI Business Listing Agent  v2.0")
    print("   Powered by Serper + Gemini + Google Sheets")
    print("="*55)
    print("  Commands:")
    print("   → best cafes in New York        (single search)")
    print("   → batch                         (run many at once)")
    print("   → history                       (view past searches)")
    print("   → quit                          (exit)")
    print("="*55 + "\n")

def get_sheet_url():
    url = os.getenv("SPREADSHEET_URL")
    if not url:
        print("⚠️  No SPREADSHEET_URL in .env! Please add it.")
        exit()
    return url

def handle_batch(sheet_url: str):
    print("\n  📦 BATCH MODE")
    print("  Enter one search per line.")
    print("  Type 'done' when finished.\n")

    queries = []
    while True:
        q = input(f"  Query {len(queries)+1}: ").strip()
        if q.lower() == "done":
            break
        if q:
            queries.append(q)

    if not queries:
        print("  ⚠️  No queries entered.\n")
        return

    print(f"\n  ✅ {len(queries)} queries queued:")
    for i, q in enumerate(queries, 1):
        print(f"     {i}. {q}")

    confirm = input("\n  Start batch? (y/n): ").strip().lower()
    if confirm == "y":
        run_batch(queries, sheet_url)
    else:
        print("  Batch cancelled.\n")

def main():
    banner()
    sheet_url = get_sheet_url()
    print(f"  📋 Sheet: {sheet_url}\n")

    while True:
        query = input("🔎 Command or search: ").strip()

        if not query:
            continue

        elif query.lower() in ["quit", "exit", "q"]:
            print("\n👋 Bye! Your data is saved in Google Sheets.\n")
            break

        elif query.lower() == "history":
            print_history()

        elif query.lower() == "batch":
            handle_batch(sheet_url)

        else:
            url = run_agent(query, sheet_url)
            if url:
                print(f"\n  🔗 Sheet: {url}\n")

if __name__ == "__main__":
    main()