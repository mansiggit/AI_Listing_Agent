from agent import run_agent
from history import save_to_history

def run_batch(queries: list, spreadsheet_url: str):
    """Run multiple queries and push all to the same sheet"""

    print(f"\n  📦 Batch mode — {len(queries)} searches queued")
    print("  " + "─"*55)

    results_summary = []

    for i, query in enumerate(queries, 1):
        query = query.strip()
        if not query:
            continue

        print(f"\n  [{i}/{len(queries)}] Starting: '{query}'")
        url = run_agent(query, spreadsheet_url)

        if url:
            results_summary.append((query, url))
            print(f"  ✅ '{query}' → done!")
        else:
            print(f"  ❌ '{query}' → failed, skipping")

    print(f"\n{'='*55}")
    print(f"  🎉 Batch Complete! {len(results_summary)}/{len(queries)} searches succeeded")
    print(f"  🔗 Sheet: {spreadsheet_url}")
    print(f"{'='*55}\n")