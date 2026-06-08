"""
app.py — FDRVC FPO Dashboard
Main Streamlit application entry point.
"""

import streamlit as st
import pandas as pd

# ── Page config MUST be first Streamlit call ─────────────
st.set_page_config(
    page_title="FDRVC FPO Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Imports ───────────────────────────────────────────────
from utils.styles       import load_css
from utils.data_loader  import load_all_data, get_last_refresh
from utils.filters      import (
    filter_by_fpo_set,
    get_all_states,
    get_all_fpo_names,
    init_132_filter,
)
from utils.helpers import find_col

from modules.overview             import show_overview
from modules.financial_analysis   import show_financial_analysis
from modules.business_turnover    import show_business_turnover
from modules.equity_grants        import show_equity_grants
from modules.management_cost      import show_management_cost
from modules.credit_loans         import show_credit_loans
from modules.licenses             import show_licenses
from modules.shareholders         import show_shareholders
from modules.operational_insights import show_operational_insights
from modules.deep_dive            import show_deep_dive

# ── CSS ───────────────────────────────────────────────────
load_css()

# ── Load data (cached — loads ONCE per server process) ───
all_data, load_errors = load_all_data()

# ── Show load warnings if any ─────────────────────────────
if load_errors:
    with st.expander("⚠️ Data Load Warnings"):
        for k, v in load_errors.items():
            st.warning(f"{k}: {v}")

# ── Refresh button ────────────────────────────────────────
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("🔄 Refresh"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

# Show last refresh time
last_refresh = get_last_refresh()
if last_refresh:
    st.sidebar.caption(f"🕒 Data as of: {last_refresh}")

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("📊 FDRVC Dashboard")

# Dataset selector
fpo_set = st.sidebar.radio("Select Dataset", ["All FPOs", "132 FPOs"])

# 132 FPO status (call once, not at module level)
init_132_filter()

# ── State & FPO filters (use cached helpers) ──────────────
# Pass the data dict as a hashable proxy — st.cache_data handles it
all_states    = get_all_states(all_data)
all_fpo_names = get_all_fpo_names(all_data)

# Narrow states/FPOs based on 132 FPO set selection
if fpo_set == "132 FPOs":
    reg = all_data.get("registration", pd.DataFrame())
    if not reg.empty:
        reg_132 = filter_by_fpo_set(reg, fpo_set)
        sc = find_col(reg_132, "state", "name")
        fc = find_col(reg_132, "fpo", "name")
        all_states    = sorted(reg_132[sc].dropna().unique()) if sc else all_states
        all_fpo_names = sorted(reg_132[fc].dropna().unique()) if fc else all_fpo_names

state_filter = st.sidebar.multiselect("Select State", all_states)
fpo_filter   = st.sidebar.multiselect("Select FPO",   all_fpo_names)

# ── Data access helpers ───────────────────────────────────

def get_df(name):
    """Return a DataFrame by name (no copy — read-only reference)."""
    return all_data.get(name, pd.DataFrame())


def fdf(name):
    """Return filtered DataFrame for the current sidebar selections."""
    df = all_data.get(name, pd.DataFrame())
    return filter_by_fpo_set(df, fpo_set, state_filter, fpo_filter)


# ── Navigation ────────────────────────────────────────────
page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Financial Analysis",
        "Business Turnover",
        "Equity Grants",
        "Management Cost",
        "Credit & Loans",
        "Licenses",
        "Shareholders",
        "Operational Insights",
        "FPO Deep Dive",
    ],
)

# ── Page routing ──────────────────────────────────────────
if page == "Overview":
    show_overview(fdf, get_df, fpo_set, state_filter, fpo_filter)

elif page == "Financial Analysis":
    show_financial_analysis(fdf, fpo_set, state_filter, fpo_filter)

elif page == "Business Turnover":
    show_business_turnover(fdf)

elif page == "Equity Grants":
    show_equity_grants(fdf)

elif page == "Management Cost":
    show_management_cost(fdf, fpo_set, state_filter, fpo_filter)

elif page == "Credit & Loans":
    show_credit_loans(fdf)

elif page == "Licenses":
    show_licenses(fdf)

elif page == "Shareholders":
    show_shareholders(fdf)

elif page == "Operational Insights":
    show_operational_insights(fdf, get_df, fpo_set, state_filter, fpo_filter)

elif page == "FPO Deep Dive":
    show_deep_dive(get_df, fpo_set)

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:#1E2B1F; margin-top:2rem;'>
<div style='text-align:center; font-size:0.68rem; color:#7A9A7E; padding: 0.4rem 0 1.2rem;'>
    🌾 10K FPO FDRVC Monitoring Dashboard &nbsp;·&nbsp; Data: 10kfpomis.dac.gov.in
    &nbsp;·&nbsp; Auto-refresh every 6 hrs &nbsp;·&nbsp; developed by Mayank Sharma
</div>
""", unsafe_allow_html=True)