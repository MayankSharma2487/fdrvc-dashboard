import requests
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.constants import *
import pandas as pd
import streamlit as st
# ─────────────────────────────────────────────
# PARALLEL DATA LOADING (fast)
# ─────────────────────────────────────────────
@st.cache_data(ttl=CACHE_DURATION_HOURS * 3600, show_spinner=False)
def load_report(name, url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
        }
        r = requests.get(url, headers=headers, timeout=90)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        if "html" in ct.lower() and len(r.content) < 50_000:
            return None, "Server returned HTML (session/auth issue)"
        df = pd.read_excel(io.BytesIO(r.content), engine="openpyxl")
        df.columns = df.columns.str.strip().str.replace("\n", " ").str.strip()
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=CACHE_DURATION_HOURS * 3600, show_spinner=False)
def load_all_data():
    """Load reports with parallelism via ThreadPoolExecutor for speed."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    data, errors = {}, {}

    def _load(item):
        k, url = item
        df, err = load_report(k, url)
        return k, df, err

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(_load, item): item[0] for item in REPORT_URLS.items()}
        for f in as_completed(futures):
            k, df, err = f.result()
            if df is not None:
                data[k] = df
            else:
                errors[k] = err
    return data, errors
