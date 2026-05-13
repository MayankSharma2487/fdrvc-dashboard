# ══════════════════════════════════════════════════════
# PAGE: FPO OPERATIONAL INSIGHTS
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_operational_insights(fdf, get_df, fpo_set, state_filter, fpo_filter):
    """
    Renders the Operational Insights dashboard.
    """
    # Fetch Data
    staff_raw     = get_df("staff")
    perf          = fdf("performance")
    lic           = fdf("license")
    profile       = fdf("profile")
    domain_expert = get_df("domain_expert")

    # --- STAFF (CEO & ACCOUNTANT) PROCESSING ---
    ceo_count = 0
    acc_count = 0
    
    if not staff_raw.empty:
        # Apply specific FPO filters to raw staff data
        staff_for_count = filter_by_fpo_set(staff_raw, fpo_set, state_filter, fpo_filter)
        fpo_reg_col_s   = find_col(staff_for_count, "fpo", "reg")
        
        if fpo_reg_col_s:
            # Filter for valid registration formats and drop duplicates
            mask = staff_for_count[fpo_reg_col_s].astype(str).str.strip().str.match(r'^U\d', na=False)
            staff_clean = staff_for_count[mask].drop_duplicates(subset=[fpo_reg_col_s], keep='last').copy()
        else:
            staff_clean = staff_for_count

        ceo_col = find_col(staff_clean, "ceo", "name")
        acc_col = find_col(staff_clean, "accountant", "name")

        def count_valid_names(series, excl_keyword):
            if series is None or series.empty:
                return 0
            # Clean and filter out placeholders like "NaN", "CEO Name", or empty strings
            s_clean = series.astype(str).str.strip().str.lower()
            mask = (
                series.notna() & 
                (s_clean != "") & 
                (s_clean != "nan") & 
                (~s_clean.str.contains(excl_keyword.lower(), na=False))
            )
            return int(mask.sum())

        ceo_count = count_valid_names(staff_clean[ceo_col] if ceo_col else None, "ceo name")
        acc_count = count_valid_names(staff_clean[acc_col] if acc_col else None, "accountant name")

    # --- GENERAL METRICS ---
    total_sh  = int(safe_sum(profile, "Total Shareholders")) if not profile.empty else 0
    total_reg = len(perf) if not perf.empty else 0

    render_kpis([
        ("CEO Count",        f"{ceo_count:,}", f"of {total_reg} FPOs"),
        ("Accountant Count", f"{acc_count:,}", f"of {total_reg} FPOs"),
        ("Total Shareholders", f"{total_sh:,}", "Members"),
        ("Total FPOs",       f"{total_reg:,}", "In dataset"),
    ])

    # --- LAYOUT: STATE BREAKDOWN & FARMER CATEGORY ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(section_header("FPOs Registered State-Wise"), unsafe_allow_html=True)
        sc = find_col(perf, "state", "name")
        if not perf.empty and sc:
            sv = perf[sc].value_counts().reset_index()
            sv.columns = ["State", "Count"]
            sv = sv.sort_values("Count", ascending=False)
            fig = px.bar(
                sv, x="State", y="Count", 
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=[COLORS["blue"]], 
                text="Count"
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Performance data or State column unavailable.")

    with c2:
        st.markdown(section_header("Farmer Category Breakdown"), unsafe_allow_html=True)
        if not profile.empty:
            farmer_cols = {
                "Small": "Small Farmers ", 
                "Marginal": "Marginal Farmer", 
                "Landless": "Landless Farmer",
                "Tenant": "Tenant Farmer", 
                "Large": "Large Farmer", 
                "Other": "Other Farmer"
            }
            farmer_data = {cat: int(safe_sum(profile, col)) for cat, col in farmer_cols.items()}
            f_df = pd.DataFrame({"Category": list(farmer_data.keys()), "Count": list(farmer_data.values())})
            f_df = f_df[f_df["Count"] > 0]
            
            if not f_df.empty:
                st.plotly_chart(pie_fig(f_df["Category"], f_df["Count"], "Farmer Categories"), use_container_width=True)
            else:
                st.info("No farmer category data found.")

    # --- LICENSE OVERVIEW ---
    st.markdown(section_header("License Coverage Overview"), unsafe_allow_html=True)
    if not lic.empty:
        rec_list = []
        not_app_list = []
        for lt in LICENSE_COLS:
            actual_col = next((c for c in lic.columns if c.strip().lower() == lt.strip().lower()), None)
            if actual_col:
                clean = lic[actual_col].astype(str).str.strip().str.lower()
                yes = int(clean.isin(["yes", "y", "1", "received"]).sum())
                rec_list.append({"License": lt.strip(), "Count": yes})
                not_app_list.append({"License": lt.strip(), "Count": len(lic) - yes})

        c3, c4 = st.columns(2)
        with c3:
            rec_df = pd.DataFrame(rec_list).sort_values("Count", ascending=True)
            fig3 = px.bar(rec_df, x="Count", y="License", orientation="h", title="Received Count",
                          template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLORS["pink"]], text="Count")
            fig3.update_traces(textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)
        with c4:
            not_app_df = pd.DataFrame(not_app_list).sort_values("Count", ascending=True)
            fig4 = px.bar(not_app_df, x="Count", y="License", orientation="h", title="Not Applied / Pending Count",
                          template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLORS["purple"]], text="Count")
            fig4.update_traces(textposition='outside')
            st.plotly_chart(fig4, use_container_width=True)

    # --- DOMAIN EXPERTS & TRAININGS ---
    st.markdown(section_header("Domain Experts & Training Activities"), unsafe_allow_html=True)
    de_tab, tr_tab = st.tabs(["Domain Experts by CBBO", "Trainings by State"])
    
    with de_tab:
        if not domain_expert.empty:
            cbbo_col_de = find_col(domain_expert, "cbbo", "name")
            if cbbo_col_de:
                de_counts = domain_expert.groupby(cbbo_col_de).size().reset_index(name="Count")
                de_counts.columns = ["CBBO Name", "Expert Count"]
                st.dataframe(de_counts.sort_values("Expert Count", ascending=False), 
                             use_container_width=True, hide_index=True)
        else:
            st.info("No Domain Expert data available.")

    with tr_tab:
        if not perf.empty:
            train_col = find_col(perf, "total", "training")
            state_col_p = find_col(perf, "state", "name")
            if train_col and state_col_p:
                train_sv = perf.groupby(state_col_p)[train_col].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).reset_index()
                train_sv.columns = ["State", "Total Trainings"]
                train_sv = train_sv[train_sv["Total Trainings"] > 0].sort_values("Total Trainings", ascending=False)
                
                fig5 = px.bar(train_sv, x="State", y="Total Trainings", 
                              template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLORS["orange"]], text="Total Trainings")
                fig5.update_traces(textposition='outside')
                fig5.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig5, use_container_width=True)