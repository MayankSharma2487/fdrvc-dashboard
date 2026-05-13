import streamlit as st
import pandas as pd
from utils.constants import MC_INSTALLMENT_MAP

def safe_num(df, col):
    if col not in df.columns:
        return pd.Series(0.0, index=df.index)
    return pd.to_numeric(df[col], errors='coerce').fillna(0.0)

def safe_sum(df, col):
    return safe_num(df, col).sum()

def find_col(df, *keywords):
    for col in df.columns:
        cl = col.lower()
        if all(k.lower() in cl for k in keywords):
            return col
    return None

def strip_header_row(df):
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

def kpi_card(label, value, sub="", clickable=False):
    cls = "kpi-card kpi-clickable" if clickable else "kpi-card"
    return f"""
    <div class="{cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def section_header(title):
    return f'<div class="section-header">{title}</div>'

def render_kpis(kpi_list):
    cols = st.columns(len(kpi_list))
    for col, kpi in zip(cols, kpi_list):
        label, val, sub = kpi[0], kpi[1], kpi[2]
        with col:
            st.markdown(kpi_card(label, val, sub), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def compute_cbbo_totals(cbbo_df):
    if cbbo_df.empty:
        return 0.0, pd.Series(dtype=float), 0

    amt_col = find_col(cbbo_df, "milestone", "cost")
    cnt_col = find_col(cbbo_df, "milestone", "received", "count") or find_col(cbbo_df, "milestone", "count")
    cost_series = pd.Series(0.0, index=cbbo_df.index)

    if amt_col:
        cost_series = pd.to_numeric(cbbo_df[amt_col], errors='coerce').fillna(0.0)

    if cost_series.sum() == 0 and cnt_col:
        counts = pd.to_numeric(cbbo_df[cnt_col], errors='coerce').fillna(0).astype(int)
        cost_series = counts * 395000.0

    return cost_series.sum(), cost_series, int((cost_series > 0).sum())

def get_mc_installment_col(mc_df, label):
    named_key, unnamed_key = MC_INSTALLMENT_MAP.get(label, (None, None))
    for c in mc_df.columns:
        cl = c.lower().strip()
        if named_key and named_key.lower() in cl and "date" not in cl and "unnamed" not in cl:
            if pd.to_numeric(mc_df[c], errors='coerce').fillna(0).sum() > 0:
                return c
    if unnamed_key and unnamed_key in mc_df.columns:
        return unnamed_key
    return None

def build_mc_installment_map(df):

    """
    Dynamically finds installment columns
    from messy MIS data.
    """

    if df.empty:
        return {}

    cols = [str(c).strip() for c in df.columns]

    inst_map = {}

    for col in cols:

        low = col.lower().replace("\n", " ").strip()

        # 1st
        if "1st" in low and "installment" in low:
            inst_map["1st"] = col

        # 2nd
        elif (
            ("2 nd" in low or "2nd" in low)
            and "installment" in low
        ):
            inst_map["2nd"] = col

        # 3rd
        elif "3rd" in low and "installment" in low:
            inst_map["3rd"] = col

        # 4th
        elif "4th" in low and "installment" in low:
            inst_map["4th"] = col

        # 5th
        elif "5th" in low and "installment" in low:
            inst_map["5th"] = col

        # 6th
        elif "6th" in low and "installment" in low:
            inst_map["6th"] = col

    return inst_map 

def calculate_grade(score):

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