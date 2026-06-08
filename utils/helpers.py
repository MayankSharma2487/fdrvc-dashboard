"""
utils/helpers.py
================
Pure Python utility functions (no Streamlit/Plotly imports).
UI rendering functions (kpi_card, render_kpis, section_header)
are in utils/charts.py only.
"""

import pandas as pd
from utils.constants import MC_INSTALLMENT_MAP


def safe_num(df, col):
    """Coerce a column to numeric, filling NaN with 0."""
    if col not in df.columns:
        return pd.Series(0.0, index=df.index)
    return pd.to_numeric(df[col], errors="coerce").fillna(0.0)


def safe_sum(df, col):
    """Sum a column safely as numeric."""
    return safe_num(df, col).sum()


def find_col(df, *keywords):
    """Find first column whose name contains ALL keywords (case-insensitive)."""
    for col in df.columns:
        cl = col.lower()
        if all(k.lower() in cl for k in keywords):
            return col
    return None


def strip_header_row(df):
    """Remove duplicate header rows embedded in data (common in BIRT exports)."""
    if df.empty:
        return df
    sr_col = find_col(df, "sr", "no")
    if sr_col:
        try:
            first_val = df.iloc[0][sr_col]
            if pd.isna(first_val):
                return df.iloc[1:].reset_index(drop=True)
            pd.to_numeric(first_val)
        except (ValueError, TypeError):
            return df.iloc[1:].reset_index(drop=True)
    return df


def compute_cbbo_totals(cbbo_df):
    """Compute total CBBO cost, per-FPO series, and FPO count."""
    if cbbo_df.empty:
        return 0.0, pd.Series(dtype=float), 0

    amt_col = find_col(cbbo_df, "milestone", "cost")
    cnt_col = find_col(cbbo_df, "milestone", "received", "count") or find_col(cbbo_df, "milestone", "count")
    cost_series = pd.Series(0.0, index=cbbo_df.index)

    if amt_col:
        cost_series = pd.to_numeric(cbbo_df[amt_col], errors="coerce").fillna(0.0)

    if cost_series.sum() == 0 and cnt_col:
        counts = pd.to_numeric(cbbo_df[cnt_col], errors="coerce").fillna(0).astype(int)
        cost_series = counts * 395000.0

    return cost_series.sum(), cost_series, int((cost_series > 0).sum())


def get_mc_installment_col(mc_df, label):
    """Find the management cost installment column for a given label."""
    named_key, unnamed_key = MC_INSTALLMENT_MAP.get(label, (None, None))
    for c in mc_df.columns:
        cl = c.lower().strip()
        if named_key and named_key.lower() in cl and "date" not in cl and "unnamed" not in cl:
            if pd.to_numeric(mc_df[c], errors="coerce").fillna(0).sum() > 0:
                return c
    if unnamed_key and unnamed_key in mc_df.columns:
        return unnamed_key
    return None


def build_mc_installment_map(df):
    """Dynamically map installment label → column name from messy MIS data."""
    if df.empty:
        return {}

    inst_map = {}
    for col in df.columns:
        low = str(col).lower().replace("\n", " ").strip()
        if "1st" in low and "installment" in low:
            inst_map["1st"] = col
        elif ("2 nd" in low or "2nd" in low) and "installment" in low:
            inst_map["2nd"] = col
        elif "3rd" in low and "installment" in low:
            inst_map["3rd"] = col
        elif "4th" in low and "installment" in low:
            inst_map["4th"] = col
        elif "5th" in low and "installment" in low:
            inst_map["5th"] = col
        elif "6th" in low and "installment" in low:
            inst_map["6th"] = col
    return inst_map


def calculate_grade(score):
    """Convert a numeric score to a letter grade (A–E)."""
    if pd.isna(score):
        return "-"
    if score < 30:
        return "E"
    elif score <= 40:
        return "D"
    elif score <= 50:
        return "C"
    elif score <= 60:
        return "B"
    return "A"