
# ══════════════════════════════════════════════════════
# PAGE: EQUITY & GRANTS
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_equity_grants(fdf):
    # Retrieve the equity dataframe
    eq = fdf("equity")
    eq_total_col = find_col(eq, "total", "equity", "grant", "released")

    # Helper to find and sum tranche columns
    def get_tranche_s(tname):
        if eq.empty:
            return None, pd.Series(dtype=float)
        for c in eq.columns:
            if tname.lower() in c.lower() and "unnamed" not in c.lower():
                s = pd.to_numeric(eq[c], errors='coerce').fillna(0)
                if s.sum() > 0:
                    return c, s
        return None, pd.Series(0, index=eq.index)

    # Calculate Tranche Values
    t1_col, t1_s = get_tranche_s("1st tranche")
    t2_col, t2_s = get_tranche_s("2nd tranche")
    t3_col, t3_s = get_tranche_s("3rd tranche")
    
    t1 = t1_s.sum() / 1e7
    t2 = t2_s.sum() / 1e7
    t3 = t3_s.sum() / 1e7
    
    # KPI Calculations
    if not eq.empty:
        total_eq = safe_sum(eq, eq_total_col) / 1e7 if eq_total_col else (t1 + t2 + t3)
        total_num_series = pd.to_numeric(eq[eq_total_col], errors='coerce').fillna(0) if eq_total_col else (t1_s + t2_s + t3_s)
        eq_fpo_count = int((total_num_series > 0).sum())
        fpo_15l = int((total_num_series >= 1500000).sum())
    else:
        total_eq = eq_fpo_count = fpo_15l = 0

    render_kpis([
        ("Total Equity Grant (Cr)", f"₹{total_eq:.2f}", "All tranches"),
        ("EG FPO Count",            f"{eq_fpo_count:,}", "Received equity"),
        ("FPOs ≥ 15L EG",           f"{fpo_15l:,}",     "High equity grant"),
    ])

    # --- TRANCHE FILTERING ---
    sel_tranche = st.selectbox("Filter by Tranche", ["All", "1st Tranche", "2nd Tranche", "3rd Tranche"], key="eq_page_tranche")
    
    if not eq.empty:
        total_series = pd.to_numeric(eq[eq_total_col], errors='coerce').fillna(0) if eq_total_col else (t1_s + t2_s + t3_s)
        disp_map = {
            "All": total_series,
            "1st Tranche": t1_s,
            "2nd Tranche": t2_s,
            "3rd Tranche": t3_s
        }
        disp = disp_map[sel_tranche]

        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(section_header(f"Equity Grant by State (Cr) — {sel_tranche}"), unsafe_allow_html=True)
            state_col = find_col(eq, "state", "name")
            if state_col:
                eq_temp = eq.copy()
                eq_temp["_disp"] = disp
                sv = eq_temp.groupby(state_col)["_disp"].sum().div(1e7).round(2).reset_index()
                sv.columns = ["State", "Equity (Cr)"]
                sv = sv[sv["Equity (Cr)"] > 0].sort_values("Equity (Cr)", ascending=True)
                
                if not sv.empty:
                    fig = px.bar(sv, x="Equity (Cr)", y="State", orientation="h",
                                template=PLOTLY_TEMPLATE,
                                color="Equity (Cr)", color_continuous_scale=["#1B6B3A", "#A5D6A7"],
                                text="Equity (Cr)")
                    fig.update_traces(texttemplate='₹%{text:.2f}Cr', textposition='outside')
                    fig.update_coloraxes(showscale=False)
                    fig.update_layout(height=450)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No equity data recorded for {sel_tranche}.")

        with c2:
            st.markdown(section_header("Tranche Comparison"), unsafe_allow_html=True)
            tr_df = pd.DataFrame({
                "Tranche":     ["1st Tranche", "2nd Tranche", "3rd Tranche"],
                "Amount (Cr)": [t1, t2, t3],
                "FPO Count":   [int((t1_s > 0).sum()), int((t2_s > 0).sum()), int((t3_s > 0).sum())]
            })
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name="Amount (Cr)", x=tr_df["Tranche"], y=tr_df["Amount (Cr)"],
                marker_color=COLORS["green2"], text=tr_df["Amount (Cr)"],
                texttemplate='₹%{text:.2f}Cr', textposition='outside'
            ))
            fig2.add_trace(go.Scatter(
                name="FPO Count", x=tr_df["Tranche"], y=tr_df["FPO Count"],
                mode="lines+markers+text", text=tr_df["FPO Count"],
                textposition='top center',
                marker=dict(color=COLORS["amber"], size=12),
                line=dict(color=COLORS["amber"], width=2), yaxis="y2"
            ))
            
            fig2.update_layout(
                yaxis=dict(title="Amount (Cr)"),
                yaxis2=dict(overlaying="y", side="right", title="FPO Count"),
                template=PLOTLY_TEMPLATE, height=440,
                legend=dict(orientation="h", y=-0.15)
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No equity grant data available.")