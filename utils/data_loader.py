"""
utils/data_loader.py
====================
Loads all FPO MIS data from local Parquet files (fast) with
Excel fallback. All data is cached for the entire session
using @st.cache_resource to avoid reloads on every rerun.

Refresh data separately using: python refresh_data.py
"""

import os
import io
import pandas as pd
import streamlit as st

PARQUET_DIR = "data/parquet"
RAW_DIR     = "data/raw"


@st.cache_resource(show_spinner="Loading FPO data...")
def load_all_data():
    """
    Loads all available datasets.
    Returns: (dict[name -> DataFrame], dict[name -> error_str])

    Uses @st.cache_resource so the data dict is shared across
    ALL users and ALL reruns — loaded exactly ONCE per server
    process. This is the single biggest performance win.
    """
    data   = {}
    errors = {}

    # ── Try Parquet first (fast) ──────────────────────────────
    if os.path.isdir(PARQUET_DIR):
        for fname in sorted(os.listdir(PARQUET_DIR)):
            if fname.endswith(".parquet"):
                name = fname.replace(".parquet", "")
                try:
                    df = pd.read_parquet(
                    os.path.join(PARQUET_DIR, fname)
                    )
                    data[name] = df
                except Exception as e:
                    errors[name] = f"Parquet read error: {e}"

    # ── Fallback: Excel for any missing datasets ──────────────
    if os.path.isdir(RAW_DIR):
        for fname in sorted(os.listdir(RAW_DIR)):
            if fname.endswith(".xlsx"):
                name = fname.replace(".xlsx", "")
                if name not in data:   # skip if already loaded from parquet
                    try:
                        df = pd.read_excel(
                            os.path.join(RAW_DIR, fname),
                            engine="openpyxl"
                        )
                        # Clean column names
                        df.columns = (
                            df.columns.astype(str)
                            .str.strip()
                            .str.replace("\n", " ", regex=False)
                        )
                        data[name] = df
                    except Exception as e:
                        errors[name] = f"Excel read error: {e}"

    return data, errors


def get_last_refresh():
    """Returns the last refresh timestamp string, or None."""
    try:
        with open("data/last_refresh.txt") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None