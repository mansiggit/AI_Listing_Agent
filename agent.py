import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from scraper import search_businesses
from sheets import push_to_sheets
from email_extractor import enrich_with_contacts
from dashboard import update_dashboard
from history import save_to_history

load_dotenv()

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1
    )

def deduplicate(businesses: list) -> list:
    seen = set()
    unique = []
    for biz in businesses:
        key = biz.get("name", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(biz)
    removed = len(businesses) - len(unique)
    if removed > 0:
        print(f"  → Removed {removed} duplicate(s)")
    return unique

def ai_enrich(llm, businesses: list, query: str) -> list:
    """Use Gemini to extract any missing phone/website and clean data"""
    sample = businesses[:8]  # only send first 8 to save tokens

    prompt = f"""You are a data cleaning assistant for business listings.
Query used: "{query}"

For the following businesses, do these tasks:
1. If 'phone' is 'N/A', try to infer it's unavailable (keep as 'N/A')
2. If 'category' is 'N/A', infer a category from the business name
3. Fix any obvious typos in business names
4. Return ONLY a valid JSON array — no markdown, no explanation

Data:
{json.dumps(sample, indent=2)}"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        enriched = json.loads(content.strip())
        # Merge enriched sample + remaining untouched businesses
        return enriched + businesses[8:]
    except Exception as e:
        print(f"  ⚠️  AI enrichment skipped (using raw data): {e}")
        return businesses

def run_agent(query: str, spreadsheet_url: str = None) -> str:
    print(f"\n{'='*55}")
    print(f"  🤖 Agent running for: \"{query}\"")
    print(f"{'='*55}")

    # Step 1: Scrape
    print("\n[1/5] 🔍 Scraping business listings...")
    businesses = search_businesses(query)

    if not businesses:
        print("  ❌ No results found. Try rephrasing your query.")
        return None

    print(f"  ✅ Found {len(businesses)} listings")

    # Step 2: Deduplicate
    print("\n[2/5] 🧹 Removing duplicates...")
    businesses = deduplicate(businesses)

    # Step 3: AI Enrichment
    print("\n[3/5] 🧠 AI enriching & cleaning data...")
    llm = get_llm()
    businesses = ai_enrich(llm, businesses, query)
    print(f"  ✅ Data cleaned — {len(businesses)} listings ready")
    
    # Step 3.5: Email extraction
    print("\n[3.5/5] 📧 Extracting emails & phones from websites...")
    businesses = enrich_with_contacts(businesses)

    # Step 4: Push to Sheets
    print("\n[4/5] 📊 Pushing to Google Sheets...")
    sheet_url = push_to_sheets(businesses, query, spreadsheet_url)
    print(f"  ✅ Done!")

    # Step 5: Update dashboard
    print("\n[5/5] 📊 Updating dashboard...")
    update_dashboard(sheet_url, query, businesses)

    # Save to local history
    save_to_history(query, len(businesses), sheet_url)

    print(f"\n{'='*55}")
    print(f"  🎉 All done! {len(businesses)} listings saved.")
    print(f"{'='*55}")

    return sheet_url