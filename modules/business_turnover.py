# ══════════════════════════════════════════════════════
# PAGE: BUSINESS TURNOVER
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *


def show_business_turnover(fdf):
    # Retrieve dataframes
    yw = fdf("yearwise_turnover")
    profile = fdf("profile")
    reg_full = fdf("registration")

    # Initialize variables
    overall_to = 0.0
    fpos_1cr = fpos_10l_1cr = fpos_zero = 0
    fpo_totals_yw = pd.Series(dtype=float)

    # Process Turnover Data
    if not yw.empty:
        yw_reg = find_col(yw, "fpo", "reg") or get_reg_col_for_df(yw)
        reg_reg_col = get_reg_col_for_df(reg_full) if not reg_full.empty else None

        if yw_reg:
            fpo_totals_yw = yw.groupby(yw_reg)["Total Turnover (INR)"].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            )
            overall_to   = fpo_totals_yw.sum() / 1e7
            fpos_1cr     = int((fpo_totals_yw >= 1e7).sum())
            fpos_10l_1cr = int(((fpo_totals_yw >= 1e6) & (fpo_totals_yw < 1e7)).sum())

            if not reg_full.empty and reg_reg_col:
                all_reg_nos = set(reg_full[reg_reg_col].dropna().astype(str).str.strip())
                fpos_with_to = set(fpo_totals_yw[fpo_totals_yw > 0].index.astype(str).str.strip())
                fpos_zero = len(all_reg_nos - fpos_with_to)
            else:
                fpos_zero = int((fpo_totals_yw == 0).sum())
        else:
            overall_to = safe_sum(yw, "Total Turnover (INR)") / 1e7

    # Calculate Activity Totals
    output_to = safe_sum(yw, "Output Activity (INR)") / 1e7
    input_to  = safe_sum(yw, "Input Activity (INR)") / 1e7
    other_to  = safe_sum(yw, "Other Activity (INR)") / 1e7

    # ── KPI row with clickable buttons ──
    col_kpis = st.columns(7)
    kpi_data_to = [
        ("Overall Turnover (Cr)", f"₹{overall_to:.2f}", "Since inception", None),
        ("Output Activity (Cr)",  f"₹{output_to:.2f}", "Total output",     None),
        ("Input Activity (Cr)",   f"₹{input_to:.2f}",  "Total input",      None),
        ("Other Activity (Cr)",   f"₹{other_to:.2f}",  "Other",            None),
        ("FPOs Revenue ≥ 1 Cr",  f"{fpos_1cr}",        "High performers",  "show_1cr_list"),
        ("FPOs 10L – 1Cr",        f"{fpos_10l_1cr}",    "Mid performers",   "show_10l_list"),
        ("FPOs Zero Revenue",     f"{fpos_zero}",        "No turnover yet",  "show_zero_list"),
    ]

    for col, (label, val, sub, toggle_key) in zip(col_kpis, kpi_data_to):
        with col:
            st.markdown(kpi_card(label, val, sub, clickable=bool(toggle_key)), unsafe_allow_html=True)
            if toggle_key:
                # Initialize state if not present
                if toggle_key not in st.session_state:
                    st.session_state[toggle_key] = False
                
                btn_label = "Hide List" if st.session_state[toggle_key] else "Show List"
                if st.button(btn_label, key=f"btn_{toggle_key}"):
                    st.session_state[toggle_key] = not st.session_state[toggle_key]
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FPO Lists Helper ──
    def get_fpo_list_for_tier(tier):
        if fpo_totals_yw.empty and tier != "zero":
            return pd.DataFrame()
        
        yw_reg = find_col(yw, "fpo", "reg") or get_reg_col_for_df(yw)
        
        if tier == "zero":
            if not reg_full.empty:
                reg_reg_col = get_reg_col_for_df(reg_full)
                if reg_reg_col:
                    all_regs = set(reg_full[reg_reg_col].dropna().astype(str).str.strip())
                    with_to  = set(fpo_totals_yw[fpo_totals_yw > 0].index.astype(str).str.strip())
                    regs_zero = list(all_regs - with_to)
                    fc = find_col(reg_full, "fpo", "name")
                    sc = find_col(reg_full, "state", "name")
                    cols_to_show = [c for c in [reg_reg_col, fc, sc, find_col(reg_full, "district", "name")] if c]
                    return reg_full[reg_full[reg_reg_col].astype(str).str.strip().isin(regs_zero)][cols_to_show].reset_index(drop=True)
            return pd.DataFrame()

        if not yw_reg: return pd.DataFrame()

        if tier == "1cr":
            regs = fpo_totals_yw[fpo_totals_yw >= 1e7].index
        elif tier == "10l":
            regs = fpo_totals_yw[(fpo_totals_yw >= 1e6) & (fpo_totals_yw < 1e7)].index
        
        yw_sub = yw.copy()
        yw_sub[yw_reg] = yw_sub[yw_reg].astype(str).str.strip()
        sub = yw_sub[yw_sub[yw_reg].isin(regs.astype(str))]
        sub = sub.drop_duplicates(subset=[yw_reg])
        
        fpo_name_col = find_col(sub, "fpo", "name")
        state_col    = find_col(sub, "state", "name")
        cols = [c for c in [yw_reg, fpo_name_col, state_col] if c]
        
        result = sub[cols].copy()
        result["Total Turnover (Cr)"] = result[yw_reg].map(lambda r: round(fpo_totals_yw.get(r, 0)/1e7, 2))
        return result.sort_values("Total Turnover (Cr)", ascending=False).reset_index(drop=True)

    # ── Display Toggled Lists ──
    if st.session_state.get("show_1cr_list"):
        st.markdown(section_header(f"FPOs with Revenue ≥ ₹1 Cr ({fpos_1cr} FPOs)"), unsafe_allow_html=True)
        df_1cr = get_fpo_list_for_tier("1cr")
        st.dataframe(df_1cr, use_container_width=True, hide_index=True)

    if st.session_state.get("show_10l_list"):
        st.markdown(section_header(f"FPOs with Revenue ₹10L – ₹1Cr ({fpos_10l_1cr} FPOs)"), unsafe_allow_html=True)
        df_10l = get_fpo_list_for_tier("10l")
        st.dataframe(df_10l, use_container_width=True, hide_index=True)

    if st.session_state.get("show_zero_list"):
        st.markdown(section_header(f"FPOs with Zero Revenue ({fpos_zero} FPOs)"), unsafe_allow_html=True)
        df_zero = get_fpo_list_for_tier("zero")
        st.dataframe(df_zero, use_container_width=True, hide_index=True)

    # ── Charts Section ──
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown(section_header("Total Revenue (Cr) State-Wise"), unsafe_allow_html=True)
        if not yw.empty:
            sc = find_col(yw, "state", "name")
            if sc:
                sv = yw.groupby(sc)["Total Turnover (INR)"].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).div(1e7).round(2).reset_index()
                sv.columns = ["State", "Revenue (Cr)"]
                sv = sv[sv["Revenue (Cr)"] > 0].sort_values("Revenue (Cr)", ascending=True)
                fig = px.bar(sv, x="Revenue (Cr)", y="State", orientation="h",
                            template=PLOTLY_TEMPLATE,
                            color="Revenue (Cr)", color_continuous_scale=["#1B6B3A", "#A5D6A7"],
                            text="Revenue (Cr)")
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig.update_coloraxes(showscale=False)
                fig.update_layout(height=480)
                st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(section_header("FY-Wise Revenue"), unsafe_allow_html=True)
        if not yw.empty and "FY Year" in yw.columns:
            fy = yw.groupby("FY Year")["Total Turnover (INR)"].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            ).div(1e7).round(2).reset_index()
            fy.columns = ["FY", "Turnover (Cr)"]
            fy = fy[fy["Turnover (Cr)"] > 0].sort_values("FY")
            st.plotly_chart(pie_fig(fy["FY"], fy["Turnover (Cr)"], "FY-wise Split"), use_container_width=True)

    with c3:
        st.markdown(section_header("Output Activity (Cr) State-Wise"), unsafe_allow_html=True)
        if not yw.empty:
            sc_yw = find_col(yw, "state", "name")
            if sc_yw and "Output Activity (INR)" in yw.columns:
                sv2 = yw.groupby(sc_yw)["Output Activity (INR)"].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).div(1e7).round(2).reset_index()
                sv2.columns = ["State", "Output (Cr)"]
                sv2 = sv2[sv2["Output (Cr)"] > 0].sort_values("Output (Cr)", ascending=False).head(12)
                fig3 = px.bar(sv2, x="State", y="Output (Cr)", template=PLOTLY_TEMPLATE,
                            color_discrete_sequence=[COLORS["amber"]], text="Output (Cr)")
                fig3.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig3.update_layout(height=480, xaxis_tickangle=-45)
                st.plotly_chart(fig3, use_container_width=True)

    c4, c5 = st.columns(2)
    with c4:
        st.markdown(section_header("Activity FY-Wise (Cr)"), unsafe_allow_html=True)
        if not yw.empty and "FY Year" in yw.columns:
            act_map = {"Output Activity (INR)": "Output", "Input Activity (INR)": "Input", "Other Activity (INR)": "Other"}
            fy_agg = {"FY Year": yw["FY Year"]}
            for col, lbl in act_map.items():
                if col in yw.columns:
                    fy_agg[lbl] = pd.to_numeric(yw[col], errors='coerce').fillna(0)
            df_fy = pd.DataFrame(fy_agg).groupby("FY Year").sum().div(1e7).reset_index()
            df_fy_m = df_fy.melt(id_vars="FY Year", var_name="Activity", value_name="Amount (Cr)")
            fig4 = px.bar(df_fy_m, x="FY Year", y="Amount (Cr)", color="Activity",
                        barmode="group", template=PLOTLY_TEMPLATE,
                        color_discrete_map={"Output": COLORS["green2"], "Input": COLORS["amber"], "Other": COLORS["teal"]})
            fig4.update_layout(height=360)
            st.plotly_chart(fig4, use_container_width=True)

    with c5:
        st.markdown(section_header("Input Activity State-Wise (Cr)"), unsafe_allow_html=True)
        if not yw.empty:
            sc_yw = find_col(yw, "state", "name")
            if sc_yw and "Input Activity (INR)" in yw.columns:
                sv3 = yw.groupby(sc_yw)["Input Activity (INR)"].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).div(1e7).round(2).reset_index()
                sv3.columns = ["State", "Input (Cr)"]
                sv3 = sv3[sv3["Input (Cr)"] > 0].sort_values("Input (Cr)", ascending=True)
                fig5 = px.bar(sv3, x="Input (Cr)", y="State", orientation="h",
                            template=PLOTLY_TEMPLATE,
                            color_discrete_sequence=[COLORS["pink"]], text="Input (Cr)")
                fig5.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig5.update_layout(height=360)
                st.plotly_chart(fig5, use_container_width=True)

    st.markdown(section_header("Other Activity Revenue (Cr) State-Wise"), unsafe_allow_html=True)
    if not yw.empty:
        sc_yw = find_col(yw, "state", "name")
        if sc_yw and "Other Activity (INR)" in yw.columns:
            sv4 = yw.groupby(sc_yw)["Other Activity (INR)"].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            ).div(1e7).round(2).reset_index()
            sv4.columns = ["State", "Other (Cr)"]
            sv4 = sv4[sv4["Other (Cr)"] > 0].sort_values("Other (Cr)", ascending=False)
            fig6 = px.bar(sv4, x="State", y="Other (Cr)", template=PLOTLY_TEMPLATE,
                        color_discrete_sequence=[COLORS["orange"]], text="Other (Cr)")
            fig6.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig6.update_layout(height=360, xaxis_tickangle=-30)
            st.plotly_chart(fig6, use_container_width=True)