import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

@st.cache_data(show_spinner=False)
def load_cbbo_manual(save_path):
    """Load manually uploaded CBBO cost file. Cached until file changes."""
    if not os.path.exists(save_path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(save_path, engine="openpyxl")
        df.columns = df.columns.str.strip().str.replace("\n", " ").str.strip()
        return strip_header_row(df)
    except Exception as e:
        st.warning(f"Manual CBBO load error: {e}")
        return pd.DataFrame()

def show_financial_analysis(fdf, fpo_set, state_filter, fpo_filter):
    # ══════════════════════════════════════════════════════
    # PAGE: FINANCIAL ANALYSIS
    # ══════════════════════════════════════════════════════
    
    # Load Dataframes
    eq = fdf("equity")
    mc = fdf("management_cost")
    cr = fdf("credit")
    cbbo = fdf("cbbo_cost")
    base = fdf("base")

    # Column Mapping & Identification
    eq_total_col = find_col(eq, "total", "equity", "grant", "released")
    mc_total_col = find_col(mc, "total", "fpo", "mgmt") or find_col(mc, "total", "fpo", "cost", "released")
    
    if mc_total_col is None and not base.empty:
        mc_total_col = find_col(base, "total", "fpo", "mgmt")

    # --- FUND CALCULATIONS ---
    total_eq = safe_sum(eq, eq_total_col) / 1e7 if eq_total_col and not eq.empty else 0
    eq_fpo_count = int((safe_num(eq, eq_total_col) > 0).sum()) if eq_total_col and not eq.empty else 0
    
    total_mc = safe_sum(mc, mc_total_col) / 1e7 if mc_total_col and not mc.empty else 0
    mc_fpo_count = int((safe_num(mc, mc_total_col) > 0).sum()) if mc_total_col and not mc.empty else 0

    # Main CBBO Logic — prefer saved manual file when it exists; fall back to
    # live API data.  We do NOT concat both blindly: if the API and the manual
    # file cover the same FPOs the totals would be double-counted.
    if os.path.exists(SAVE_PATH):
        try:
            cbbo_manual = pd.read_excel(SAVE_PATH, engine="openpyxl")
            cbbo_manual.columns = (cbbo_manual.columns.str.strip().str.replace("\n", " ").str.strip())
            cbbo_manual = strip_header_row(cbbo_manual)
            cbbo_manual = filter_by_fpo_set(cbbo_manual, fpo_set, state_filter, fpo_filter)
            # Use manual file as primary; add only live rows for FPOs NOT in manual file
            manual_reg_col = find_col(cbbo_manual, "fpo", "reg") or find_col(cbbo_manual, "reg")
            live_reg_col   = find_col(cbbo, "fpo", "reg") or find_col(cbbo, "reg")
            if manual_reg_col and live_reg_col and not cbbo.empty:
                manual_regs = set(cbbo_manual[manual_reg_col].dropna().astype(str).str.strip())
                cbbo_extra  = cbbo[~cbbo[live_reg_col].astype(str).str.strip().isin(manual_regs)]
                final_cbbo_df = pd.concat([cbbo_manual, cbbo_extra], ignore_index=True)
            else:
                # Can't isolate reg-no columns — manual file is authoritative
                final_cbbo_df = cbbo_manual
        except Exception as e:
            st.warning(f"Manual CBBO merge error: {e}")
            final_cbbo_df = cbbo.copy()
    else:
        final_cbbo_df = cbbo.copy()

    final_cbbo_total, final_cost_series, final_cbbo_count = compute_cbbo_totals(final_cbbo_df)
    total_cbbo = final_cbbo_total / 1e7

    # Loan Data
    loan_amt_col = "Loan Sanctioned Amount (INR)"
    total_loan = safe_sum(cr, loan_amt_col) / 1e7 if not cr.empty else 0
    loan_fpo_count = int((safe_num(cr, loan_amt_col) > 0).sum()) if not cr.empty else 0

    # Total Aggregation
    total_fund = total_eq + total_mc + total_cbbo

    render_kpis([
        ("Total Fund Released (Cr)",    f"₹{total_fund:.2f}", "EG + MC + CBBO"),
        ("Equity Grant Released (Cr)",  f"₹{total_eq:.2f}",   f"{eq_fpo_count} FPOs"),
        ("FPO Mgmt Cost Released (Cr)", f"₹{total_mc:.2f}",   f"{mc_fpo_count} FPOs"),
        ("CBBO Cost Released (Cr)",     f"₹{total_cbbo:.2f}", f"{final_cbbo_count} FPOs"),
        ("Loan Received FPOs",          f"{loan_fpo_count:,}", "Credit linked"),
        ("Loan Received (Cr)",          f"₹{total_loan:.2f}", "Total sanctioned"),
    ])

    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Equity Grant", "💼 FPO Mgmt Cost", "🏢 CBBO Cost", "🏦 Credit & Loans"])

    # ── TAB 1: EQUITY ──
    with tab1:
        sel_tranche = st.selectbox("Select Tranche", ["All", "1st Tranche", "2nd Tranche", "3rd Tranche"], key="eq_tranche_fa")
        if not eq.empty and eq_total_col:
            def get_tr_s(tname):
                for c in eq.columns:
                    if tname.lower() in c.lower() and "unnamed" not in c.lower():
                        s = pd.to_numeric(eq[c], errors='coerce').fillna(0)
                        if s.sum() > 0: return s
                return pd.Series(0, index=eq.index)

            t1_s, t2_s, t3_s = get_tr_s("1st tranche"), get_tr_s("2nd tranche"), get_tr_s("3rd tranche")
            
            disp_map = {"All": safe_num(eq, eq_total_col), "1st Tranche": t1_s, "2nd Tranche": t2_s, "3rd Tranche": t3_s}
            
            render_kpis([
                ("1st Tranche (Cr)", f"₹{t1_s.sum()/1e7:.2f}", f"{(t1_s>0).sum()} FPOs"),
                ("2nd Tranche (Cr)", f"₹{t2_s.sum()/1e7:.2f}", f"{(t2_s>0).sum()} FPOs"),
                ("3rd Tranche (Cr)", f"₹{t3_s.sum()/1e7:.2f}", f"{(t3_s>0).sum()} FPOs"),
            ])

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(section_header(f"EG State-Wise (Cr) — {sel_tranche}"), unsafe_allow_html=True)
                scol = find_col(eq, "state", "name")
                if scol:
                    eq["_amt"] = disp_map[sel_tranche]
                    sv = eq.groupby(scol)["_amt"].sum().div(1e7).round(2).reset_index(name="Cr")
                    sv = sv[sv["Cr"] > 0].sort_values("Cr")
                    fig = px.bar(sv, x="Cr", y=scol, orientation="h", template=PLOTLY_TEMPLATE, text="Cr",
                                 color="Cr", color_continuous_scale=["#1B6B3A", "#A5D6A7"])
                    fig.update_layout(height=450, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown(section_header("Tranche Comparison"), unsafe_allow_html=True)
                tr_df = pd.DataFrame({
                    "Tranche": ["1st", "2nd", "3rd"],
                    "Amount (Cr)": [t1_s.sum()/1e7, t2_s.sum()/1e7, t3_s.sum()/1e7],
                    "FPO Count": [int((t1_s>0).sum()), int((t2_s>0).sum()), int((t3_s>0).sum())]
                })
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(name="Amount (Cr)", x=tr_df["Tranche"], y=tr_df["Amount (Cr)"], marker_color=COLORS["green2"], text=tr_df["Amount (Cr)"].round(2), textposition='outside'))
                fig2.add_trace(go.Scatter(name="FPO Count", x=tr_df["Tranche"], y=tr_df["FPO Count"], mode="lines+markers+text", text=tr_df["FPO Count"], yaxis="y2"))
                fig2.update_layout(yaxis2=dict(overlaying="y", side="right"), template=PLOTLY_TEMPLATE, height=440)
                st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 2: MANAGEMENT COST ──
    with tab2:
        if not mc.empty:
            sel_inst = st.selectbox("Select Installment", ["All", "1st", "2nd", "3rd", "4th", "5th", "6th"], key="mc_inst_fa")
            inst_cols_mc = build_mc_installment_map(mc)
            
            if sel_inst == "All":
                disp_mc_amt = safe_num(mc, mc_total_col)
            elif sel_inst in inst_cols_mc:
                disp_mc_amt = pd.to_numeric(mc[inst_cols_mc[sel_inst]], errors='coerce').fillna(0)
            else:
                disp_mc_amt = pd.Series(0, index=mc.index)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(section_header(f"Mgmt Cost State-Wise (Cr)"), unsafe_allow_html=True)
                scol = find_col(mc, "state", "name")
                if scol:
                    mc["_disp"] = disp_mc_amt
                    sv = mc.groupby(scol)["_disp"].sum().div(1e7).round(2).reset_index(name="Cr")
                    sv = sv[sv["Cr"] > 0].sort_values("Cr")
                    fig_mc = px.bar(

                    sv,

                    x="Cr",
                    y=scol,

                    orientation="h",

                    template=PLOTLY_TEMPLATE,

                    color="Cr",

                    color_continuous_scale=[
                        "#163A24",
                        "#1B6B3A",
                        "#2E8B57",
                        "#66BB6A",
                        "#A5D6A7"
                    ],

                    text="Cr"
                )

                fig_mc.update_traces(
                    texttemplate='₹%{text:.2f}',
                    textposition='outside'
                )
                fig_mc.update_layout(
                    height=450,
                    coloraxis_showscale=False,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20
                    )
                )
                st.plotly_chart(
                    fig_mc,
                    use_container_width=True
                )

            with c2:
                st.markdown(section_header("Installment Summary"), unsafe_allow_html=True)
                ins_data = [{"Installment": l, "Cr": round(pd.to_numeric(mc[c], errors='coerce').sum()/1e7, 2)} for l, c in inst_cols_mc.items()]
                st.dataframe(pd.DataFrame(ins_data), use_container_width=True, hide_index=True)

    # ── TAB 3: CBBO COST ──
    with tab3:
        if not final_cbbo_df.empty:
            final_cbbo_df["_cost"] = final_cost_series
            avg_cbbo = (final_cbbo_total / max(len(final_cbbo_df), 1)) / 1e5
            
            render_kpis([
                ("CBBO Cost (Cr)", f"₹{total_cbbo:.2f}", "Total released"),
                ("FPOs with Cost", f"{final_cbbo_count:,}", "Released"),
                ("Avg Cost / FPO (L)", f"₹{avg_cbbo:.1f}L", "Release rate"),
            ])

            st.markdown(section_header("CBBO FPO-wise Details"), unsafe_allow_html=True)
            st.dataframe(final_cbbo_df[[c for c in final_cbbo_df.columns if "_cost" not in c and "unnamed" not in c.lower()]], use_container_width=True, hide_index=True)
        
        st.divider()
        uploaded = st.file_uploader("📤 Upload CBBO Cost Excel", type=["xlsx"])
        if uploaded:
            with open(SAVE_PATH, "wb") as f: f.write(uploaded.getbuffer())
            st.success("File uploaded successfully! Refreshing...")
            st.rerun()

    # ── TAB 4: CREDIT ──
    with tab4:
        if not cr.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(section_header("Loan Type Distribution"), unsafe_allow_html=True)
                lt_col = find_col(cr, "type", "loan")
                if lt_col:
                    lt = cr.groupby(lt_col)[loan_amt_col].sum().div(1e7).reset_index(name="Cr")
                    st.plotly_chart(pie_fig(lt[lt_col], lt["Cr"], "Loan Split"), use_container_width=True)

            with c2:
                st.markdown(section_header("Loans by State"), unsafe_allow_html=True)
                scol = find_col(cr, "state", "name")
                if scol:
                    sv = cr.groupby(scol)[loan_amt_col].sum().div(1e7).reset_index(name="Cr")
                    st.plotly_chart(bar_h(sv.sort_values("Cr"), "Cr", scol, "", COLORS["teal"]), use_container_width=True)