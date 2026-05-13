import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────
from utils.styles import load_css
from utils.data_loader import load_all_data
from utils.filters import *
from utils.helpers import *
from utils.filters import filter_by_fpo_set

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────
from modules.overview import show_overview
from modules.financial_analysis import show_financial_analysis
from modules.business_turnover import show_business_turnover
from modules.equity_grants import show_equity_grants
from modules.management_cost import show_management_cost
from modules.credit_loans import show_credit_loans
from modules.licenses import show_licenses
from modules.shareholders import show_shareholders
from modules.operational_insights import show_operational_insights
from modules.deep_dive import show_deep_dive


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FDRVC FPO Dashboard",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────
load_css()

# ─────────────────────────────────────────────
# REFRESH BUTTON
# ─────────────────────────────────────────────

col1, col2 = st.columns([8, 1])

with col2:

    if st.button("🔄 Refresh"):

        st.cache_data.clear()

        st.rerun()  
# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
all_data, load_errors = load_all_data()

# ─────────────────────────────────────────────
# SHOW LOAD WARNINGS
# ─────────────────────────────────────────────
if load_errors:

    with st.expander("⚠️ Data Load Warnings"):

        for k, v in load_errors.items():
            st.warning(f"{k}: {v}")

# ─────────────────────────────────────────────
# GET DF FUNCTION
# ─────────────────────────────────────────────
def get_df(name):

    return all_data.get(name, pd.DataFrame()).copy()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("📊 FDRVC Dashboard")

# DATASET SELECTOR
fpo_set = st.sidebar.radio(
    "Select Dataset",
    [
        "All FPOs",
        "132 FPOs"
    ]
)

# ─────────────────────────────────────────────
# FILTER BASE
# ─────────────────────────────────────────────
filter_base_df = get_df("registration")

filter_base_df = filter_by_fpo_set(
    filter_base_df,
    fpo_set
)

# ─────────────────────────────────────────────
# STATES
# ─────────────────────────────────────────────
state_col_filter = find_col(
    filter_base_df,
    "state",
    "name"
)

if state_col_filter:

    all_states = sorted(
        filter_base_df[state_col_filter]
        .dropna()
        .unique()
        .tolist()
    )

else:

    all_states = []

# ─────────────────────────────────────────────
# STATE FILTER
# ─────────────────────────────────────────────
state_filter = st.sidebar.multiselect(
    "Select State",
    all_states
)

# ─────────────────────────────────────────────
# APPLY STATE FILTER
# ─────────────────────────────────────────────
if state_filter and state_col_filter:

    filter_base_df = filter_base_df[
        filter_base_df[state_col_filter]
        .isin(state_filter)
    ]

# ─────────────────────────────────────────────
# FPO NAMES
# ─────────────────────────────────────────────
fpo_col_filter = find_col(
    filter_base_df,
    "fpo",
    "name"
)

if fpo_col_filter:

    all_fpo_names = sorted(
        filter_base_df[fpo_col_filter]
        .dropna()
        .unique()
        .tolist()
    )

else:

    all_fpo_names = []

# ─────────────────────────────────────────────
# FPO FILTER
# ─────────────────────────────────────────────
fpo_filter = st.sidebar.multiselect(
    "Select FPO",
    all_fpo_names
)

# ─────────────────────────────────────────────
# FILTER FUNCTION
# ─────────────────────────────────────────────
def fdf(name):

    df = get_df(name)

    df = filter_by_fpo_set(
        df,
        fpo_set,
        state_filter,
        fpo_filter
    )

    return df

# ─────────────────────────────────────────────
# PAGE NAVIGATION
# ─────────────────────────────────────────────
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
        "FPO Deep Dive"
    ]
)

# ─────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────
if page == "Overview":

    show_overview(

    fdf,

    get_df,

    fpo_set,

    state_filter,

    fpo_filter
)

elif page == "Financial Analysis":

    show_financial_analysis(
        fdf,
        fpo_set,
        state_filter,
        fpo_filter
    )

elif page == "Business Turnover":

    show_business_turnover(
        fdf
    )

elif page == "Equity Grants":

    show_equity_grants(
        fdf
    )

elif page == "Management Cost":

    show_management_cost(
                fdf,

                fpo_set,

                state_filter,

                fpo_filter
    )

elif page == "Credit & Loans":

    show_credit_loans(
        fdf
    )

elif page == "Licenses":

    show_licenses(
        fdf
    )

elif page == "Shareholders":

    show_shareholders(
        fdf
    )

elif page == "Operational Insights":

    show_operational_insights(
        fdf,
        get_df,
        fpo_set,
        state_filter,
        fpo_filter
    )

elif page == "FPO Deep Dive":

    show_deep_dive(
        get_df,
        fpo_set
    )

    # ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<hr style='border-color:#1E2B1F; margin-top:2rem;'>
<div style='text-align:center; font-size:0.68rem; color:#7A9A7E; padding: 0.4rem 0 1.2rem;'>
    🌾 10K FPO FDRVC Monitoring Dashboard &nbsp;·&nbsp; Data: 10kfpomis.dac.gov.in
    &nbsp;·&nbsp; Auto-refresh every 6 hrs &nbsp;·&nbsp; developed by Mayank Sharma
</div>
""", unsafe_allow_html=True)