import streamlit as st
import os
from dotenv import load_dotenv
from agent import run_agent, deduplicate, ai_enrich, get_llm
from history import load_history, save_to_history

load_dotenv()

st.set_page_config(
    page_title="AI Listing Agent",
    page_icon="🏢",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* Apply Poppins everywhere */
    * {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Pure black background */
    .stApp { background-color: #000000; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* Main content */
    .main .block-container {
        background-color: #000000;
        padding: 2rem;
    }

    /* All text */
    h1, h2, h3, p, label, .stMarkdown {
        color: #f0f0f0 !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Input box */
    .stTextInput > div > div > input {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-size: 15px !important;
        font-family: 'Poppins', sans-serif !important;
        padding: 12px !important;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #555555 !important;
        box-shadow: 0 0 0 2px rgba(255,255,255,0.05) !important;
    }

    /* Search button */
    .stButton > button {
        background-color: #ffffff !important;
        color: #0000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        width: 100%;
        letter-spacing: 0.03em;
    }
    .stButton > button:hover {
        background-color: #e0e0e0 !important;
        color: #0000
        transform: scale(1.02);
        transition: all 0.2s ease;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 14px !important;
        padding: 1.2rem 1.4rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #888888 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricDelta"] { color: #888888 !important; }

    /* Dataframe / Table */
    [data-testid="stDataFrame"] {
        border: 1px solid #222222 !important;
        border-radius: 14px !important;
        overflow: hidden;
    }
    .stDataFrame th {
        background-color: #111111 !important;
        color: #888888 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    .stDataFrame td {
        background-color: #0a0a0a !important;
        color: #e0e0e0 !important;
        font-size: 13px !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ffffff, #aaaaaa) !important;
        border-radius: 4px !important;
    }
    .stProgress {
        background-color: #222222 !important;
        border-radius: 4px !important;
    }

    /* Status dots */
    .dot-green {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #4caf82;
        margin-right: 8px;
    }
    .dot-amber {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #f0a500;
        margin-right: 8px;
    }

    /* Success box */
    .stSuccess {
        background-color: #0a1a0f !important;
        border: 1px solid #2a6644 !important;
        border-radius: 10px !important;
        color: #5DCAA5 !important;
    }

    /* Alert/info box */
    .stAlert {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
    }

    /* Radio nav buttons */
    [data-testid="stRadio"] label {
        font-size: 14px !important;
        font-weight: 400 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        cursor: pointer;
    }
    [data-testid="stRadio"] label:hover {
        background-color: #1a1a1a !important;
    }

    /* Text area */
    .stTextArea textarea {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Divider */
    hr { border-color: #222222 !important; }

    /* Caption */
    .stCaption { color: #555555 !important; }

    /* Links */
    a { color: #aaaaaa !important; text-decoration: underline; }
    a:hover { color: #ffffff !important; }

    /* Page title + sub */
    .page-header {
        font-size: 30px;
        font-weight: 600;
        color: #ffffff !important;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    .page-subheader {
        font-size: 13px;
        color: #555555 !important;
        font-weight: 300;
        margin-bottom: 1.5rem;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #ffffff !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #555555; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏢 AI Listing Agent")
    st.caption("v2.0 — Powered by Serper + Gemini")
    st.divider()
    page = st.radio(
        "Navigation",
        ["🔍 Search", "📦 Batch Search", "📜 History"],
        label_visibility="visible"
    )
    st.divider()
    sheet_url = os.getenv("SPREADSHEET_URL", "")
    if sheet_url:
        st.caption("SHEET")
        st.markdown("AI Business Listings")
        st.markdown(f"[Open in Google Sheets]({sheet_url})")
    else:
        st.warning("No SPREADSHEET_URL in .env!")

# ── Search Page ──────────────────────────────────────────
if page == "🔍 Search":
    st.markdown('<p class="page-header">Search Businesses</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subheader">Type a query and hit Search — results go straight to your Google Sheet</p>', unsafe_allow_html=True)

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input("query", placeholder="e.g. best cafes in New York", label_visibility="collapsed")
    with col_btn:
        search_btn = st.button("Search", type="primary", use_container_width=True)

    if search_btn and query:
        st.divider()
        progress   = st.progress(0)
        status_log = st.empty()
        logs       = []

        def log(msg, dot="green"):
            dot_html = f'<span class="dot-{dot}"></span>'
            logs.append(f'{dot_html} {msg}')
            status_log.markdown("<br>".join(logs), unsafe_allow_html=True)

        from scraper import search_businesses
        log(f"Scraping listings for: <b>{query}</b>")
        progress.progress(15)
        businesses = search_businesses(query)

        if not businesses:
            st.error("No results found. Try rephrasing your query.")
            st.stop()

        log(f"Found <b>{len(businesses)}</b> listings")
        progress.progress(30)

        businesses = deduplicate(businesses)
        log(f"Duplicates removed — <b>{len(businesses)}</b> unique listings")
        progress.progress(45)

        llm = get_llm()
        businesses = ai_enrich(llm, businesses, query)
        log("AI enrichment complete")
        progress.progress(60)

        from email_extractor import enrich_with_contacts
        log(f"Extracting emails & phones from websites...", dot="amber")
        businesses = enrich_with_contacts(businesses)
        progress.progress(75)

        from sheets import push_to_sheets
        log("Pushing to Google Sheets...", dot="amber")
        result_url = push_to_sheets(businesses, query, sheet_url)
        progress.progress(88)

        from dashboard import update_dashboard
        log("Updating dashboard...", dot="amber")
        update_dashboard(result_url, query, businesses)
        save_to_history(query, len(businesses), result_url)
        progress.progress(100)

        log("All done! 🎉")
        st.divider()

        # ── Metrics ──────────────────────────────────────
        has_email  = sum(1 for b in businesses if b.get("email",   "N/A") != "N/A")
        has_phone  = sum(1 for b in businesses if b.get("phone",   "N/A") != "N/A")
        ratings    = [float(b.get("rating", 0)) for b in businesses if b.get("rating") and b.get("rating") != "N/A"]
        avg_rating = round(sum(ratings)/len(ratings), 1) if ratings else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Found",   len(businesses), "listings")
        m2.metric("Avg Rating",    avg_rating,      "out of 5")
        m3.metric("Emails Found",  f"{has_email}/{len(businesses)}")
        m4.metric("Phones Found",  f"{has_phone}/{len(businesses)}")

        st.divider()

        # ── Results Table ─────────────────────────────────
        st.subheader("📋 Results Preview")
        st.markdown(f"[📊 Open Google Sheet]({result_url})")
        import pandas as pd
        df = pd.DataFrame([{
            "Business Name": b.get("name",     ""),
            "Rating":        b.get("rating",   ""),
            "Category":      b.get("category", ""),
            "Phone":         b.get("phone",    "N/A"),
            "Email":         b.get("email",    "N/A"),
            "Website":       b.get("website",  "N/A"),
            "Address":       b.get("address",  ""),
        } for b in businesses])
        st.dataframe(df, use_container_width=True, hide_index=True)

# ── Batch Search Page ────────────────────────────────────
elif page == "📦 Batch Search":
    st.markdown('<p class="page-header">Batch Search</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subheader">Run multiple searches at once — all saved to the same sheet</p>', unsafe_allow_html=True)

    queries_text = st.text_area(
        "Enter one search per line",
        placeholder="best cafes in New York\ntop gyms in London\nitalian restaurants in Paris",
        height=200
    )

    if st.button("🚀 Run Batch", type="primary"):
        queries = [q.strip() for q in queries_text.strip().split("\n") if q.strip()]
        if not queries:
            st.warning("Please enter at least one query.")
        else:
            progress = st.progress(0)
            for i, q in enumerate(queries):
                with st.spinner(f"[{i+1}/{len(queries)}] Searching: {q}"):
                    run_agent(q, sheet_url)
                progress.progress((i+1) / len(queries))
            st.success(f"✅ Batch complete! {len(queries)} searches done.")
            st.markdown(f"[📊 Open Google Sheet]({sheet_url})")

# ── History Page ─────────────────────────────────────────
elif page == "📜 History":
    st.markdown('<p class="page-header">Search History</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subheader">All your past searches</p>', unsafe_allow_html=True)

    history = load_history()
    if not history:
        st.info("No searches yet — go run your first search!")
    else:
        import pandas as pd
        df = pd.DataFrame(list(reversed(history)))
        df.columns = ["Query", "Results", "Sheet URL", "Searched At"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total searches: {len(history)}")