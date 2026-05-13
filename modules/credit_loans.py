# ══════════════════════════════════════════════════════
# PAGE: CREDIT & LOANS
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_credit_loans(fdf):
    # Retrieve the credit dataframe
    cr = fdf("credit")

    # --- KPI CALCULATIONS ---
    if not cr.empty:
        total_loan = safe_sum(cr, "Loan Sanctioned Amount (INR)") / 1e7
        # Convert to numeric first to count non-zero loans
        loan_series = pd.to_numeric(cr["Loan Sanctioned Amount (INR)"], errors='coerce').fillna(0)
        loan_count  = int((loan_series > 0).sum())
        
        avg_loan = (total_loan * 1e7 / max(loan_count, 1)) / 1e5
        
        cg_col = find_col(cr, "cg", "cover")
        cg_yes = int(cr[cg_col].astype(str).str.lower().str.strip().isin(["yes"]).sum()) if cg_col else 0
    else:
        total_loan = loan_count = avg_loan = cg_yes = 0

    render_kpis([
        ("Total Loans Sanctioned (Cr)", f"₹{total_loan:.2f}", "Credit linked"),
        ("Loan Received FPO Count",     f"{loan_count:,}",    "FPOs with loan"),
        ("Avg Loan Size (L)",           f"₹{avg_loan:.1f}L",  "Per FPO"),
        ("CG Cover Availed",            f"{cg_yes:,}",         "FPOs"),
    ])

    # --- VISUALIZATIONS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(section_header("Loans by State (Cr)"), unsafe_allow_html=True)
        sc = find_col(cr, "state", "name")
        if sc and not cr.empty:
            sv = cr.groupby(sc)["Loan Sanctioned Amount (INR)"].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            ).div(1e7).round(2).reset_index()
            sv.columns = ["State", "Loan (Cr)"]
            sv = sv[sv["Loan (Cr)"] > 0].sort_values("Loan (Cr)", ascending=True)
            
            if not sv.empty:
                st.plotly_chart(bar_h(sv, "Loan (Cr)", "State", "", COLORS["teal"]), use_container_width=True)
            else:
                st.info("No loan data available by state.")

    with c2:
        st.markdown(section_header("Loan Type Split"), unsafe_allow_html=True)
        lt_col = find_col(cr, "type", "loan")
        if lt_col and not cr.empty:
            lt = cr.groupby(lt_col)["Loan Sanctioned Amount (INR)"].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            ).div(1e7).round(2).reset_index()
            lt.columns = ["Loan Type", "Amount (Cr)"]
            lt = lt[lt["Amount (Cr)"] > 0]
            
            if not lt.empty:
                st.plotly_chart(pie_fig(lt["Loan Type"], lt["Amount (Cr)"], "By Loan Type"), use_container_width=True)
            else:
                st.info("No loan type data available.")

    # --- DATA TABLE ---
    if not cr.empty:
        st.markdown(section_header("Credit Records"), unsafe_allow_html=True)
        # Select first 100 records for performance
        st.dataframe(cr.head(100), use_container_width=True, hide_index=True)
    else:
        st.warning("No credit records found for the current filters.")