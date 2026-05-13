# ─────────────────────────────────────────────
# 132 FPO LIST LOADING & FILTERS
# ─────────────────────────────────────────────
import streamlit as st
import pandas as pd
import os

# Import your helpers and constants
from utils.helpers import find_col
from utils.constants import CACHE_DURATION_HOURS

@st.cache_data(show_spinner=False)
def load_fpo_132():
    paths = ["fpo_132.xlsx", "data/fpo_132.xlsx", "fpo_132.csv", "FPO_132.xlsx"]
    for p in paths:
        if os.path.exists(p):
            try:
                if p.endswith(".csv"):
                    df = pd.read_csv(p)
                else:
                    df = pd.read_excel(p, engine="openpyxl")
                df.columns = df.columns.str.strip()
                return df
            except Exception as e:
                st.warning(f"Could not read {p}: {e}")
    return None

# Initialize meta data
df_132_meta = load_fpo_132()
fpo_132_reg_nos = set()

# Process 132 FPO Filter Setup
if df_132_meta is not None:
    reg_col_132 = None
    # Try exact column name matches
    for c in df_132_meta.columns:
        if c.strip().lower() in ["fpo_reg_no", "fpo reg no", "fpo reg no.", "fpo reg id", "company reg no", "company_reg_no"]:
            reg_col_132 = c
            break
    
    # Fallback: CIN pattern match (U followed by digits)
    if reg_col_132 is None:
        for c in df_132_meta.columns:
            sample = df_132_meta[c].dropna().astype(str).str.strip()
            if sample.str.match(r'^U\d').any():
                reg_col_132 = c
                break

    if reg_col_132:
        fpo_132_reg_nos = set(df_132_meta[reg_col_132].dropna().astype(str).str.strip().tolist())
        st.sidebar.markdown(
            f"<div style='font-size:0.7rem;color:#2E9E5B;'>✅ 132 FPO file loaded ({len(fpo_132_reg_nos)} reg nos)</div>",
            unsafe_allow_html=True
        )
    else:
        st.sidebar.warning("⚠️ Could not find reg no column in fpo_132.xlsx")
else:
    st.sidebar.info("ℹ️ Place fpo_132.xlsx in app folder to enable 132 FPO filter")

# ─────────────────────────────────────────────
# REG COL FINDER & DEDUP
# ─────────────────────────────────────────────
def get_reg_col_for_df(df):
    for c in df.columns:
        cl = c.lower().strip()
        if cl in ["fpo reg no", "fpo reg no.", "fpo reg id", "company reg no",
                  "fpo_reg_no", "company reg no.", "fpo reg id.", "fpo reg no  "]:
            return c
    
    for patterns in [("fpo", "reg", "no"), ("fpo", "reg", "id"), ("company", "reg", "no"), ("fpo", "reg")]:
        c = find_col(df, *patterns)
        if c:
            return c
            
    # Final check for CIN string pattern
    for c in df.columns:
        try:
            sample = df[c].dropna().astype(str).str.strip()
            if sample.str.match(r'^U\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$').mean() > 0.25:
                return c
        except Exception:
            pass
    return None

def deduplicate_fpos(df):
    if df.empty:
        return df
    reg_col = get_reg_col_for_df(df)
    if reg_col and reg_col in df.columns:
        temp = df.copy()
        temp[reg_col] = temp[reg_col].astype(str).str.strip()
        temp = temp[temp[reg_col].str.match(r'^U\d', na=False)]
        temp = temp.drop_duplicates(subset=[reg_col], keep="last")
        return temp
    return df

def filter_by_fpo_set(df, fpo_set_choice, state_filter=None, fpo_filter=None):
    if df.empty:
        return df
    result = df.copy()

    # Apply 132 FPO filter
    if fpo_set_choice == "132 FPOs" and fpo_132_reg_nos:
        reg_col = get_reg_col_for_df(result)
        if reg_col:
            mask = result[reg_col].astype(str).str.strip().isin(fpo_132_reg_nos)
            result = result[mask].reset_index(drop=True)
        else:
            if df_132_meta is not None and "FPO Name" in df_132_meta.columns:
                fpo_names_132 = set(df_132_meta["FPO Name"].dropna().astype(str).str.strip().tolist())
                fc = find_col(result, "fpo", "name")
                if fc:
                    mask = result[fc].astype(str).str.strip().isin(fpo_names_132)
                    result = result[mask].reset_index(drop=True)
        
        result = deduplicate_fpos(result)

    # State Filter
    if state_filter and len(state_filter) > 0:
        sc = find_col(result, "state")
        if sc:
            result = result[result[sc].isin(state_filter)].reset_index(drop=True)

    # FPO Name Filter
    if fpo_filter and len(fpo_filter) > 0:
        fc = find_col(result, "fpo", "name")
        if fc:
            result = result[result[fc].isin(fpo_filter)].reset_index(drop=True)

    return result

@st.cache_data(ttl=CACHE_DURATION_HOURS * 3600, show_spinner=False)
def get_all_states(_all_data):
    reg = _all_data.get("registration", pd.DataFrame())
    if reg.empty: return []
    sc = find_col(reg, "state", "name")
    return sorted(reg[sc].dropna().unique().tolist()) if sc else []

@st.cache_data(ttl=CACHE_DURATION_HOURS * 3600, show_spinner=False)
def get_all_fpo_names(_all_data):
    reg = _all_data.get("registration", pd.DataFrame())
    if reg.empty: return []
    fc = find_col(reg, "fpo", "name")
    return sorted(reg[fc].dropna().unique().tolist()) if fc else []
