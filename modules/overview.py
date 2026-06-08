# ══════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_overview(fdf,get_df,fpo_set,state_filter,fpo_filter):
    """
    Renders the high-level dashboard overview with key performance indicators.
    """
    # Fetch Dataframes
    reg     = fdf("registration")
    profile = fdf("profile")
    yw      = fdf("yearwise_turnover")
    eq      = fdf("equity")
    mc      = fdf("management_cost")
    cr      = fdf("credit")
    cbbo    = fdf("cbbo_cost")
    score_df = fdf("score")

    # ─────────────────────────────────────────────
    # SCORE + GRADE
    # ─────────────────────────────────────────────

    overall_avg_score = 0
    overall_grade = "-"

    if not score_df.empty:

        score_col = find_col(
            score_df,
            "total",
            "score"
        ) or find_col(
            score_df,
            "total",
            "average"
        )

        if score_col:

            score_df["_score"] = pd.to_numeric(
                score_df[score_col],
                errors="coerce"
            )

            overall_avg_score = round(
                score_df["_score"].mean(),
                2
            )

            overall_grade = calculate_grade(
                overall_avg_score
            )

    # --- CORE METRIC CALCULATIONS ---
    total_fpos = len(reg) if not reg.empty else 0


    # 1. Overall Turnover (Deduplicated per FPO and Financial Year)
    overall_to = 0.0
    if not yw.empty:
        yw_reg = find_col(yw, "fpo", "reg") or get_reg_col_for_df(yw)
        if yw_reg:
            yw_c = yw.copy()
            yw_c["_to"] = pd.to_numeric(yw_c.get("Total Turnover (INR)", 0), errors='coerce').fillna(0)
            # Drop duplicates to avoid double-counting the same FPO in the same FY
            subset_cols = [yw_reg]
            if "FY Year" in yw_c.columns:
                subset_cols.append("FY Year")
            yw_c = yw_c.drop_duplicates(subset=subset_cols)
            overall_to = yw_c["_to"].sum() / 1e7

    # 2. Equity Grant
    eq_total_col = find_col(eq, "total", "equity", "grant", "released")
    total_eq     = safe_sum(eq, eq_total_col) / 1e7 if eq_total_col and not eq.empty else 0
    eq_fpo_count = int((safe_num(eq, eq_total_col) > 0).sum()) if eq_total_col and not eq.empty else 0

    # 3. Management Cost (Fallback to base if mc is missing)
    mc_total_col = find_col(mc, "total", "fpo", "mgmt") or find_col(mc, "total", "fpo", "cost", "released")
    base_df = fdf("base")
    if mc_total_col is None and not base_df.empty:
        mc_total_col = find_col(base_df, "total", "fpo", "mgmt")
    
    source_df = mc if (mc_total_col and not mc.empty) else base_df
    total_mc = safe_sum(source_df, mc_total_col) / 1e7 if mc_total_col else 0

    # 4. CBBO Costs — prefer saved manual file; fall back to live API data.
    # Do NOT add both together: that double-counts FPOs present in both sources.
    if os.path.exists(SAVE_PATH):

        try:

            cbbo_m = pd.read_excel(
                SAVE_PATH,
                engine="openpyxl"
            )

            cbbo_m.columns = (
                cbbo_m.columns
                .str.strip()
                .str.replace("\n", " ")
                .str.strip()
            )

            cbbo_m = strip_header_row(cbbo_m)

            # APPLY SIDEBAR FILTERS
            cbbo_m = filter_by_fpo_set(

                cbbo_m,

                fpo_set,
                state_filter,
                fpo_filter
            )

            # Merge manual (authoritative) + live rows for FPOs not in manual
            manual_reg_col = find_col(cbbo_m, "fpo", "reg") or find_col(cbbo_m, "reg")
            live_reg_col   = find_col(cbbo, "fpo", "reg") or find_col(cbbo, "reg")
            if manual_reg_col and live_reg_col and not cbbo.empty:
                manual_regs = set(cbbo_m[manual_reg_col].dropna().astype(str).str.strip())
                cbbo_extra  = cbbo[~cbbo[live_reg_col].astype(str).str.strip().isin(manual_regs)]
                import pandas as _pd
                cbbo_final = _pd.concat([cbbo_m, cbbo_extra], ignore_index=True)
            else:
                cbbo_final = cbbo_m

            cbbo_total_inr, _, _ = compute_cbbo_totals(cbbo_final)
            total_cbbo = cbbo_total_inr / 1e7

        except Exception as e:

            st.sidebar.error(
                f"Error loading manual CBBO file: {e}"
            )
            cbbo_total_inr, _, _ = compute_cbbo_totals(cbbo)
            total_cbbo = cbbo_total_inr / 1e7

    else:
        cbbo_total_inr, _, _ = compute_cbbo_totals(cbbo)
        total_cbbo = cbbo_total_inr / 1e7

    # 5. Combined Totals
    total_fund = total_eq + total_mc + total_cbbo
    total_cr   = safe_sum(cr, "Loan Sanctioned Amount (INR)") / 1e7
    total_sh   = int(safe_sum(profile, "Total Shareholders")) if not profile.empty else 0
    loan_fpo_count = int((safe_num(cr, "Loan Sanctioned Amount (INR)") > 0).sum()) if not cr.empty else 0

    # --- KPI DISPLAY ---
    render_kpis([
        ("Total FPOs",          f"{total_fpos:,}",      "Registered"),
        ("Overall Turnover",    f"₹{overall_to:.2f} Cr", "Since Inception"),
        ("FDRVC Grade",         overall_grade,              f"Score: {overall_avg_score}"),
        ("Avg Performance",     f"{overall_avg_score}",     "Overall Score"),
        ("Total Fund Released", f"₹{total_fund:.2f} Cr", "EG + MC + CBBO"),
        ("Equity Grant",        f"₹{total_eq:.2f} Cr",  "Distributed"),
        ("Mgmt Cost",           f"₹{total_mc:.2f} Cr",  "Released"),
        ("Credit Sanctioned",   f"₹{total_cr:.2f} Cr",  "Loan Amount"),
        ("Total Shareholders",  f"{total_sh:,}",        "Farmer Members"),

    ])

    render_kpis([
        ("EG Recipient FPOs",   f"{eq_fpo_count:,}",    "Equity Linked"),
        ("Credit Linked FPOs",  f"{loan_fpo_count:,}",   "Loan Sanctioned"),
    ])

    # --- VISUALIZATIONS ---
    c1, c2 = st.columns([1.6, 1])
    
    with c1:
        st.markdown(section_header("No. of FPOs State-Wise"), unsafe_allow_html=True)
        sc_col = find_col(reg, "state", "name")
        if not reg.empty and sc_col:
            sc = reg[sc_col].value_counts().reset_index()
            sc.columns = ["State", "Count"]
            sc = sc.sort_values("Count", ascending=True)
            fig = px.bar(sc, x="Count", y="State", orientation="h",
                         template=PLOTLY_TEMPLATE,
                         color="Count", color_continuous_scale=["#1B6B3A", "#66BB6A"],
                         text="Count")
            fig.update_traces(textposition='outside')
            fig.update_coloraxes(showscale=False)
            fig.update_layout(height=500, margin=dict(l=20, r=40, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(section_header("Registration Trend"), unsafe_allow_html=True)
        date_col = find_col(reg, "date", "registration")
        if not reg.empty and date_col:
            reg["_year"] = pd.to_datetime(reg[date_col], errors='coerce').dt.year
            yr = reg["_year"].value_counts().sort_index().reset_index()
            yr.columns = ["Year", "Count"]
            yr = yr.dropna(subset=["Year"])
            yr["Year"] = yr["Year"].astype(int).astype(str)
            fig2 = px.bar(yr, x="Year", y="Count", template=PLOTLY_TEMPLATE,
                          color_discrete_sequence=[COLORS["amber"]], text="Count")
            fig2.update_traces(textposition='outside')
            fig2.update_layout(height=500)
            st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    
    with c3:
        st.markdown(section_header("Top 15 States by Revenue (Cr)"), unsafe_allow_html=True)
        if not yw.empty:
            sc_yw = find_col(yw, "state", "name")
            if sc_yw:
                sv = yw.groupby(sc_yw)["Total Turnover (INR)"].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).div(1e7).round(2).reset_index()
                sv.columns = ["State", "Revenue (Cr)"]
                sv = sv[sv["Revenue (Cr)"] > 0].sort_values("Revenue (Cr)", ascending=False).head(15)
                
                fig3 = px.bar(sv, x="State", y="Revenue (Cr)", template=PLOTLY_TEMPLATE,
                              color_discrete_sequence=[COLORS["teal"]], text="Revenue (Cr)")
                fig3.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig3.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig3, use_container_width=True)

    with c4:

        st.markdown(
            section_header(
                "Grade as per Score"
            ),
            unsafe_allow_html=True
        )

        if not score_df.empty:

            state_col_s = find_col(
                score_df,
                "state"
            )

            score_col = find_col(
                score_df,
                "total",
                "score"
            ) or find_col(
                score_df,
                "total",
                "average"
            )

            if state_col_s and score_col:

                score_df["_score"] = pd.to_numeric(
                    score_df[score_col],
                    errors="coerce"
                )

                grade_summary = (
                    score_df
                    .groupby(state_col_s)["_score"]
                    .mean()
                    .round(2)
                    .reset_index()
                )

                grade_summary["Grade"] = (
                    grade_summary["_score"]
                    .apply(calculate_grade)
                )

                grade_summary.columns = [
                    "State",
                    "Avg Score",
                    "Grade"
                ]

                st.dataframe(
                    grade_summary.sort_values(
                        "Avg Score",
                        ascending=False
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "Scoring data not available."
            )