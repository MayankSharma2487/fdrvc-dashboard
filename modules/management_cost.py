# ══════════════════════════════════════════════════════
# PAGE: MANAGEMENT COST (MODULAR - FIXED)
# ══════════════════════════════════════════════════════

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ⚠️ IMPORTANT: These imports MUST match your actual module paths
# Adjust these based on your folder structure
from utils.filters import filter_by_fpo_set
from utils.helpers import (
    safe_num,
    safe_sum,
    find_col,
    strip_header_row,
    build_mc_installment_map,
    compute_cbbo_totals
)
from utils.charts import section_header
from utils.constants import PLOTLY_TEMPLATE, COLORS, SAVE_PATH


@st.cache_data(show_spinner=False)
def _get_mc_installment_map(col_tuple):
    """Cache installment column detection by DataFrame column signature."""
    import pandas as pd
    dummy_df = pd.DataFrame(columns=list(col_tuple))
    return build_mc_installment_map(dummy_df)

def show_management_cost(fdf,

    fpo_set,

    state_filter,

    fpo_filter):
    """
    Renders the Management Cost and CBBO Cost analysis dashboard.
    
    Args:
        fdf (callable): Function that takes a report name and returns filtered DataFrame
                       Should be: fdf = lambda name: get_df(name) after applying filters
    
    Example usage in main app:
        def fdf(name):
            df = get_df(name)
            return filter_by_fpo_set(df, fpo_set, state_filter, fpo_filter)
        
        show_management_cost(fdf)
    """

    # ─────────────────────────────────────
    # FETCH DATA via fdf() - this applies all filters
    # ─────────────────────────────────────

    mc = fdf("management_cost").copy()

    # CLEAN COLUMN NAMES
    mc.columns = (
        mc.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
    )

    # REMOVE HEADER ROWS INSIDE DATA

    # RESET INDEX
    mc = mc.reset_index(drop=True)
    
    # Fetch CBBO data
    cbbo = fdf("cbbo_cost")

    if mc.empty and cbbo.empty:
        st.info("No cost data available.")
        return

    # ─────────────────────────────────────
    # MANAGEMENT COST CALCULATIONS
    # ─────────────────────────────────────

    # Find the total MC column
    mc_total_col = (
        find_col(mc, "total", "fpo", "mgmt")
        or
        find_col(mc, "total", "fpo", "cost", "released")
    )

    total_mc = (
        safe_sum(mc, mc_total_col) / 1e7
        if mc_total_col and not mc.empty
        else 0
    )

    # UNIQUE FPO COUNT
    fpo_col_mc = find_col(mc, "fpo", "name")

    if fpo_col_mc and not mc.empty:
        mc_fpo_count = mc[fpo_col_mc].nunique()
    else:
        mc_fpo_count = 0

    # AVERAGE COST
    avg_mc = (
        (total_mc * 100) / mc_fpo_count
        if mc_fpo_count > 0
        else 0
    )

    # ─────────────────────────────────────
    # CBBO DATA HANDLING
    # ─────────────────────────────────────

    final_cbbo_df = cbbo.copy()

    # Load and merge manual CBBO file if exists
    if os.path.exists(SAVE_PATH):
        try:
            cbbo_manual = pd.read_excel(
                SAVE_PATH,
                engine="openpyxl"
            )

            cbbo_manual.columns = (
                cbbo_manual.columns
                .str.strip()
                .str.replace("\n", " ")
                .str.strip()
            )

            cbbo_manual = strip_header_row(
            cbbo_manual
            )

            # APPLY SIDEBAR FILTERS
            cbbo_manual = filter_by_fpo_set(

                cbbo_manual,
                fpo_set,
                state_filter,
                fpo_filter
            )

            final_cbbo_df = pd.concat(

                [final_cbbo_df, cbbo_manual],

                ignore_index=True
            )

        except Exception as e:
            st.warning(f"CBBO file load error: {e}")

    # CBBO TOTALS
    cbbo_total_inr, cbbo_cost_series, cbbo_count = compute_cbbo_totals(
        final_cbbo_df
    )

    total_cbbo = cbbo_total_inr / 1e7
    total_fund_mc = total_mc + total_cbbo

    # ─────────────────────────────────────
    # KPI SECTION
    # ─────────────────────────────────────

    col_kpi = st.columns(5)
    kpi_data = [
        ("Total FPO Mgmt Cost (Cr)", f"₹{total_mc:.2f}", "All installments"),
        ("CBBO Cost Released (Cr)", f"₹{total_cbbo:.2f}", "Milestone costs"),
        ("Total MC + CBBO (Cr)", f"₹{total_fund_mc:.2f}", "Combined"),
        ("Mgmt Cost FPO Count", f"{mc_fpo_count:,}", "Unique FPOs"),
        ("Avg Cost / FPO (L)", f"₹{avg_mc:.2f}L", "Per FPO"),
    ]
    
    for col, (label, val, sub) in zip(col_kpi, kpi_data):
        with col:
            st.markdown(
                f"""
                <div style='background:var(--surface2); border:1px solid var(--border); border-radius:12px; 
                            padding:1rem; text-align:center; border-left:3px solid var(--accent);'>
                    <div style='font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; 
                                letter-spacing:0.1em; margin-bottom:0.3rem;'>{label}</div>
                    <div style='font-family:Fraunces,serif; font-size:1.4rem; font-weight:700; 
                                color:white; margin-bottom:0.2rem;'>{val}</div>
                    <div style='font-size:0.7rem; color:var(--text-muted);'>{sub}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────
    # INSTALLMENT FILTER
    # ─────────────────────────────────────

    sel_inst = st.selectbox(
        "Select Installment View",
        ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"],
        key="mc_page_inst"
    )

    # Build installment column mapping
    inst_cols_mc = (
        build_mc_installment_map(mc)
        if not mc.empty
        else {}
    )

    # DEBUG: Show what installments were found
    if not inst_cols_mc:
        st.warning("⚠️ No installment columns found in data. Available columns: " + 
                   ", ".join(mc.columns[:5]))

    c1, c2 = st.columns(2)

    # ─────────────────────────────────────
    # STATE WISE MC
    # ─────────────────────────────────────

    with c1:
        st.markdown(
            section_header(f"Mgmt Cost by State (Cr) — {sel_inst}"),
            unsafe_allow_html=True
        )

        state_col = find_col(mc, "state", "name")

        if state_col and not mc.empty:
            
            # ✅ CREATE ISOLATED COPY FOR STATE SECTION
            mc_state = mc.copy()

            # Determine which column to display
            if sel_inst == "All" and mc_total_col:
                mc_state["_disp_mc"] = safe_num(mc_state, mc_total_col)
                
            elif sel_inst in inst_cols_mc:
                col_to_use = inst_cols_mc[sel_inst]
                raw_col = mc_state[col_to_use]

                # HANDLE DUPLICATE COLUMN NAMES
                if isinstance(raw_col, pd.DataFrame):
                    raw_col = raw_col.iloc[:, 0]

                mc_state["_disp_mc"] = (
                    pd.to_numeric(raw_col, errors="coerce")
                    .fillna(0)
                    .astype(float)
                )
            else:
                mc_state["_disp_mc"] = 0

            # Group and aggregate
            sv = (
                mc_state.groupby(state_col)["_disp_mc"]
                .sum()
                .div(1e7)
                .round(2)
                .reset_index()
            )

            sv.columns = ["State", "Cost (Cr)"]
            sv = sv[sv["Cost (Cr)"] > 0].sort_values("Cost (Cr)", ascending=True)

            if sv.empty:
                st.warning(f"❌ No data available for {sel_inst} installment")
            else:
                fig = px.bar(
                    sv,
                    x="Cost (Cr)",
                    y="State",
                    orientation="h",
                    template=PLOTLY_TEMPLATE,
                    color="Cost (Cr)",
                    color_continuous_scale=["#4A148C", "#CE93D8"],
                    text="Cost (Cr)"
                )

                fig.update_traces(
                    texttemplate='%{text:.2f}',
                    textposition='outside'
                )

                fig.update_coloraxes(showscale=False)
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=40, t=20, b=20)
                )

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("State column not found in data")

    # ─────────────────────────────────────
    # INSTALLMENT SUMMARY
    # ─────────────────────────────────────

    with c2:
        st.markdown(
            section_header("Installment-Wise Summary"),
            unsafe_allow_html=True
        )

        if inst_cols_mc and not mc.empty:
            
            installs = []

            for label, col in inst_cols_mc.items():
                try:
                    # ✅ CREATE FRESH COPY FOR EACH INSTALLMENT
                    mc_inst = mc.copy()

                    # Get the column
                    raw_col = mc_inst[col]

                    # HANDLE DUPLICATE COLUMNS
                    if isinstance(raw_col, pd.DataFrame):
                        raw_col = raw_col.iloc[:, 0]

                    amt_series = (
                        pd.to_numeric(raw_col, errors="coerce")
                        .fillna(0)
                        .astype(float)
                    )

                    installs.append({
                        "Installment": label,
                        "Amount (Cr)": round(amt_series.sum() / 1e7, 2),
                        "FPO Count": int((amt_series > 0).sum())
                    })

                except Exception as e:
                    st.warning(f"⚠️ {label} installment error: {e}")

            # PREVENT EMPTY DF ERROR
            if len(installs) > 0:

                ins_df = pd.DataFrame(installs)

                fig2 = go.Figure()

                fig2.add_trace(
                    go.Bar(
                        name="Amount (Cr)",
                        x=ins_df["Installment"],
                        y=ins_df["Amount (Cr)"],
                        marker_color=COLORS["purple"],
                        text=ins_df["Amount (Cr)"],
                        texttemplate='₹%{text:.2f}',
                        textposition='outside'
                    )
                )

                fig2.add_trace(
                    go.Scatter(
                        name="FPO Count",
                        x=ins_df["Installment"],
                        y=ins_df["FPO Count"],
                        mode="lines+markers+text",
                        text=ins_df["FPO Count"],
                        textposition='top center',
                        marker=dict(
                            color=COLORS["amber"],
                            size=10
                        ),
                        line=dict(
                            color=COLORS["amber"],
                            width=3
                        ),
                        yaxis="y2"
                    )
                )

                fig2.update_layout(
                    yaxis=dict(title="Amount (Cr)"),
                    yaxis2=dict(
                        overlaying="y",
                        side="right",
                        title="FPO Count"
                    ),
                    template=PLOTLY_TEMPLATE,
                    height=410,
                    legend=dict(orientation="h", y=-0.2),
                    margin=dict(l=20, r=20, t=20, b=20)
                )

                st.plotly_chart(fig2, use_container_width=True)

            else:
                st.warning("❌ No installment data found.")

        else:
            st.warning("No installment columns available")

    # ─────────────────────────────────────
    # CBBO STATE WISE
    # ─────────────────────────────────────

    if not final_cbbo_df.empty and cbbo_total_inr > 0:

        st.markdown(
            section_header("CBBO Cost State-Wise (Cr)"),
            unsafe_allow_html=True
        )

        cbbo_state_col = find_col(final_cbbo_df, "state")

        if cbbo_state_col:

            final_cbbo_df["_cost"] = cbbo_cost_series

            sv_cbbo = (
                final_cbbo_df.groupby(cbbo_state_col)["_cost"]
                .sum()
                .div(1e7)
                .round(2)
                .reset_index()
            )

            sv_cbbo.columns = ["State", "CBBO Cost (Cr)"]
            sv_cbbo = sv_cbbo[sv_cbbo["CBBO Cost (Cr)"] > 0].sort_values(
                "CBBO Cost (Cr)", ascending=True
            )

            fig_cbbo = px.bar(
                sv_cbbo,
                x="CBBO Cost (Cr)",
                y="State",
                orientation="h",
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=[COLORS["orange"]],
                text="CBBO Cost (Cr)"
            )

            fig_cbbo.update_traces(
                texttemplate='%{text:.2f}',
                textposition='outside'
            )

            fig_cbbo.update_layout(height=450)

            st.plotly_chart(fig_cbbo, use_container_width=True)