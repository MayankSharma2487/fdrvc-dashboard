"""
utils/filters.py
================
FPO filtering utilities. All module-level side effects
(Streamlit widgets) have been removed — call
init_132_filter(sidebar_container) once from app.py.
"""

import os
import pandas as pd
import streamlit as st
from utils.helpers import find_col
from utils.constants import CACHE_DURATION_HOURS


# ─────────────────────────────────────────────────────────
# 132 FPO LIST — loaded once, cached
# ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_fpo_132():
    """Load the 132-FPO reference file. Returns DataFrame or None."""
    paths = [
        "fpo_132.xlsx",
        "data/fpo_132.xlsx",
        "fpo_132.csv",
        "FPO_132.xlsx",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p) if p.endswith(".csv") else pd.read_excel(p, engine="openpyxl")
                df.columns = df.columns.str.strip()
                return df
            except Exception:
                pass
    return None


@st.cache_data(show_spinner=False)
def get_fpo_132_reg_nos():
    """Returns a frozenset of 132 FPO registration numbers."""
    df = load_fpo_132()
    if df is None:
        return frozenset()

    # Try exact column name matches
    for c in df.columns:
        if c.strip().lower() in ["fpo_reg_no", "fpo reg no", "fpo reg no.", "fpo reg id", "company reg no", "company_reg_no"]:
            return frozenset(df[c].dropna().astype(str).str.strip().tolist())

    # Fallback: CIN pattern match
    for c in df.columns:
        sample = df[c].dropna().astype(str).str.strip()
        if sample.str.match(r"^U\d").any():
            return frozenset(df[c].dropna().astype(str).str.strip().tolist())

    return frozenset()


def init_132_filter(sidebar_container=None):
    """
    Call once from app.py to render the 132 FPO status message.
    Separated from module level to avoid duplicate widget renders.
    """
    reg_nos = get_fpo_132_reg_nos()
    target = sidebar_container or st.sidebar

    if reg_nos:
        target.markdown(
            f"<div style='font-size:0.7rem;color:#2E9E5B;'>✅ 132 FPO file loaded ({len(reg_nos)} reg nos)</div>",
            unsafe_allow_html=True,
        )
    else:
        target.info("ℹ️ Place fpo_132.xlsx in app folder to enable 132 FPO filter")


# ─────────────────────────────────────────────────────────
# COLUMN FINDERS — cached per DataFrame shape signature
# ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _get_reg_col_cached(col_tuple):
    """
    Internal: find the registration number column given a tuple of column names.
    Cached so repeated calls on the same DataFrame are instant.
    """
    col_list = list(col_tuple)
    # Exact matches first
    for c in col_list:
        cl = c.lower().strip()
        if cl in ["fpo reg no", "fpo reg no.", "fpo reg id", "company reg no",
                  "fpo_reg_no", "company reg no.", "fpo reg id.", "fpo reg no  "]:
            return c

    # Keyword combos
    for patterns in [("fpo", "reg", "no"), ("fpo", "reg", "id"), ("company", "reg", "no"), ("fpo", "reg")]:
        for c in col_list:
            cl = c.lower()
            if all(k in cl for k in patterns):
                return c

    return None


def get_reg_col_for_df(df):
    """Find registration number column for a DataFrame. Cached by column names."""
    if df.empty:
        return None
    return _get_reg_col_cached(tuple(df.columns.tolist()))


def deduplicate_fpos(df):
    """Remove duplicate FPO rows, keeping the last entry per registration number."""
    if df.empty:
        return df
    reg_col = get_reg_col_for_df(df)
    if reg_col and reg_col in df.columns:
        mask = df[reg_col].astype(str).str.strip().str.match(r"^U\d", na=False)
        return df[mask].drop_duplicates(subset=[reg_col], keep="last")
    return df



# Datasets that have multiple rows per FPO (one row per FY / installment / etc.)
# Deduplication must be skipped for these — keeping only one row per reg no would
# destroy data (e.g. all-but-last-FY turnover entries would be silently dropped).
_MULTI_ROW_DATASETS = frozenset([
    "yearwise_turnover",
    "management_cost",
    "cbbo_cost",
])

# Global registry so filter_by_fpo_set can decide whether to deduplicate.
# Populated by calling tag_dataframe() before filtering.
_df_tag_registry: dict = {}


def tag_dataframe(df, dataset_name: str):
    """
    Tag a DataFrame with its source dataset name so filter_by_fpo_set can
    decide whether deduplication is safe.  Call this once in data_loader.py
    right after loading each dataset.
    """
    _df_tag_registry[id(df)] = dataset_name


def _is_multi_row_dataset(df) -> bool:
    """Return True if df comes from a dataset that has multiple rows per FPO."""
    return _df_tag_registry.get(id(df), "") in _MULTI_ROW_DATASETS


def filter_by_fpo_set(
    df,
    fpo_set_choice,
    state_filter=None,
    fpo_filter=None
):
    """
    Apply:
    - Dataset filter (All vs 132 FPOs)
    - State filter
    - FPO filter

    Avoid deduplicating turnover / installment datasets.
    """

    if df.empty:
        return df

    mask = pd.Series(True, index=df.index)

    # --------------------------------------------------
    # 132 FPO FILTER
    # --------------------------------------------------
    if fpo_set_choice == "132 FPOs":

        fpo_132_reg_nos = get_fpo_132_reg_nos()

        if fpo_132_reg_nos:

            reg_col = get_reg_col_for_df(df)

            if reg_col:

                mask &= (
                    df[reg_col]
                    .astype(str)
                    .str.strip()
                    .isin(fpo_132_reg_nos)
                )

            else:

                df_132 = load_fpo_132()

                if (
                    df_132 is not None
                    and "FPO Name" in df_132.columns
                ):

                    names_132 = set(
                        df_132["FPO Name"]
                        .dropna()
                        .astype(str)
                        .str.strip()
                    )

                    fc = find_col(
                        df,
                        "fpo",
                        "name"
                    )

                    if fc:

                        mask &= (
                            df[fc]
                            .astype(str)
                            .str.strip()
                            .isin(names_132)
                        )

    # --------------------------------------------------
    # STATE FILTER
    # --------------------------------------------------
    if state_filter:

        sc = find_col(df, "state")

        if sc:

            mask &= df[sc].isin(state_filter)

    # --------------------------------------------------
    # FPO FILTER
    # --------------------------------------------------
    if fpo_filter:

        fc = find_col(
            df,
            "fpo",
            "name"
        )

        if fc:

            mask &= df[fc].isin(fpo_filter)

    result = df.loc[mask]

    # --------------------------------------------------
    # DEDUPLICATE ONLY TRUE MASTER TABLES
    # --------------------------------------------------
    should_skip_dedupe = any(
        col in result.columns
        for col in [
            "FY Year",
            "Total Turnover (INR)",
            "Output Activity (INR)",
            "Input Activity (INR)",
            "Other Activity (INR)"
        ]
    )

    if (
        fpo_set_choice == "132 FPOs"
        and not should_skip_dedupe
    ):
        result = deduplicate_fpos(result)

    return result.reset_index(drop=True)


@st.cache_data(ttl=CACHE_DURATION_HOURS * 3600, show_spinner=False)
def get_all_states(_all_data):
    reg = _all_data.get("registration", pd.DataFrame())
    if reg.empty:
        return []
    sc = find_col(reg, "state", "name")
    return sorted(reg[sc].dropna().unique().tolist()) if sc else []


@st.cache_data(ttl=CACHE_DURATION_HOURS * 3600, show_spinner=False)
def get_all_fpo_names(_all_data):
    reg = _all_data.get("registration", pd.DataFrame())
    if reg.empty:
        return []
    fc = find_col(reg, "fpo", "name")
    return sorted(reg[fc].dropna().unique().tolist()) if fc else []