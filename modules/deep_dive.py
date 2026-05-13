
# ══════════════════════════════════════════════════════
# PAGE: FPO DEEP DIVE
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_deep_dive(get_df, fpo_set):
    # Retrieve all required datasets
    perf = get_df("performance")
    yw_all = get_df("yearwise_turnover")
    eq_all = get_df("equity")
    cr_all = get_df("credit")
    lic_all = get_df("license")
    staff_all = get_df("staff")
    params_all = get_df("parameters")

    if not perf.empty:
        state_col = find_col(perf, "state", "name")
        fpo_name_col = find_col(perf, "fpo", "name")
        perf_f = filter_by_fpo_set(perf, fpo_set)

        # --- SELECTION FILTERS ---
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            states = ["All"] + (sorted(perf_f[state_col].dropna().unique().tolist()) if state_col else [])
            sel_state = st.selectbox("Filter by State", states)

        df_filt = perf_f if sel_state == "All" else perf_f[perf_f[state_col] == sel_state]

        with col_f2:
            fpo_names = sorted(df_filt[fpo_name_col].dropna().unique().tolist()) if fpo_name_col else []
            sel_fpo = st.selectbox("Select FPO", fpo_names if fpo_names else ["No data"])

        # --- FPO DETAIL VIEW ---
        if sel_fpo and fpo_name_col and sel_fpo != "No data":
            fpo_rows = df_filt[df_filt[fpo_name_col] == sel_fpo]
            
            if not fpo_rows.empty:
                fpo_row = fpo_rows.iloc[0]
                fpo_reg_col = find_col(perf, "fpo", "reg")
                fpo_reg = str(fpo_row[fpo_reg_col]).strip() if fpo_reg_col else None

                st.markdown(f"### 🌾 {sel_fpo}")

                # 1. Profile Information Grid
                info_fields = [
                    (find_col(perf, "state", "name"), "State"),
                    (find_col(perf, "district", "name"), "District"),
                    (find_col(perf, "block", "name"), "Block"),
                    (fpo_reg_col, "Reg No"),
                    (find_col(perf, "primary", "crop"), "Primary Crop"),
                    (find_col(perf, "allocation", "category"), "Category"),
                ]
                
                detail_html = '<div style="display:grid; grid-template-columns: repeat(3,1fr); gap:0.8rem; background:rgba(122, 154, 126, 0.1); border-radius:10px; padding:1.2rem; border:1px solid #7A9A7E; margin-bottom:1rem;">'
                for col_name, label in info_fields:
                    if col_name and col_name in fpo_row.index:
                        val = fpo_row[col_name]
                        if pd.notna(val) and str(val).lower() not in ["nan", "nat", ""]:
                            detail_html += f'<div><div style="font-size:0.68rem;color:#7A9A7E;text-transform:uppercase;letter-spacing:0.05em;">{label}</div><div style="font-weight:600;font-size:0.88rem;">{val}</div></div>'
                detail_html += '</div>'
                st.markdown(detail_html, unsafe_allow_html=True)

                # 2. Key Staff
                if fpo_reg and not staff_all.empty:
                    sreg_col = find_col(staff_all, "fpo", "reg")
                    if sreg_col:
                        staff_fpo = staff_all[staff_all[sreg_col].astype(str).str.strip() == fpo_reg]
                        if not staff_fpo.empty:
                            ceo_col = find_col(staff_fpo, "ceo", "name")
                            acc_col = find_col(staff_fpo, "accountant", "name")
                            s1, s2 = st.columns(2)
                            with s1:
                                if ceo_col: st.metric("CEO", str(staff_fpo[ceo_col].iloc[0]))
                            with s2:
                                if acc_col: st.metric("Accountant", str(staff_fpo[acc_col].iloc[0]))

                # 3. Financial Overview
                st.markdown(section_header("Financial Overview"), unsafe_allow_html=True)
                fin_cols_list = st.columns(4)

                # Equity Grant Calculation
                eq_val_display = "—"
                if fpo_reg and not eq_all.empty:
                    eq_reg_col = find_col(eq_all, "fpo", "reg")
                    if eq_reg_col:
                        eq_fpo = eq_all[eq_all[eq_reg_col].astype(str).str.strip() == fpo_reg]
                        if not eq_fpo.empty:
                            eq_tc = find_col(eq_fpo, "total", "equity", "grant")
                            if eq_tc:
                                eq_val = safe_sum(eq_fpo, eq_tc)
                                eq_val_display = f"₹{eq_val/1e7:.2f} Cr" if eq_val >= 1e7 else f"₹{eq_val/1e5:.2f} L"

                # Loan Calculation
                loan_display = "—"
                if fpo_reg and not cr_all.empty:
                    cr_reg_col = find_col(cr_all, "fpo", "reg")
                    if cr_reg_col:
                        cr_fpo = cr_all[cr_all[cr_reg_col].astype(str).str.strip() == fpo_reg]
                        if not cr_fpo.empty:
                            loan_val = safe_sum(cr_fpo, "Loan Sanctioned Amount (INR)")
                            loan_display = f"₹{loan_val/1e5:.2f} L" if loan_val > 0 else "Not Availed"

                kpis = [("Equity Grant", eq_val_display, ""), ("Loan Sanctioned", loan_display, "")]
                for c_idx, (label, display, sub) in enumerate(kpis):
                    with fin_cols_list[c_idx]:
                        st.markdown(kpi_card(label, display, sub), unsafe_allow_html=True)

                # 4. Year-wise Turnover Chart
                if fpo_reg and not yw_all.empty:
                    yw_reg_col = find_col(yw_all, "fpo", "reg")
                    if yw_reg_col:
                        fpo_yw = yw_all[yw_all[yw_reg_col].astype(str).str.strip() == fpo_reg]
                        if not fpo_yw.empty and "FY Year" in fpo_yw.columns:
                            st.markdown(section_header("Year-wise Turnover"), unsafe_allow_html=True)
                            cols_to_use = ["FY Year", "Output Activity (INR)", "Input Activity (INR)", "Other Activity (INR)", "Total Turnover (INR)"]
                            fy_data = fpo_yw[[c for c in cols_to_use if c in fpo_yw.columns]].copy()
                            
                            # Clean numeric columns
                            num_cols = ["Output Activity (INR)", "Input Activity (INR)", "Other Activity (INR)", "Total Turnover (INR)"]
                            for col in num_cols:
                                if col in fy_data.columns:
                                    fy_data[col] = pd.to_numeric(fy_data[col], errors='coerce').fillna(0)
                            
                            fy_data = fy_data[fy_data["Total Turnover (INR)"] > 0]
                            if not fy_data.empty:
                                fy_data_m = fy_data.melt(id_vars="FY Year", 
                                                       value_vars=[c for c in num_cols if c != "Total Turnover (INR)"],
                                                       var_name="Activity", value_name="Amount")
                                fy_data_m["Amount (L)"] = fy_data_m["Amount"] / 1e5
                                fy_data_m["Activity"] = fy_data_m["Activity"].str.replace(" (INR)", "", regex=False)
                                
                                fig_fy = px.bar(fy_data_m, x="FY Year", y="Amount (L)", color="Activity",
                                               barmode="group", template=PLOTLY_TEMPLATE,
                                               color_discrete_map={"Output Activity": COLORS["green2"],
                                                                   "Input Activity": COLORS["amber"],
                                                                   "Other Activity": COLORS["teal"]})
                                fig_fy.update_layout(height=320, yaxis_title="Lakhs")
                                st.plotly_chart(fig_fy, use_container_width=True)

                # 5. Licenses
                if fpo_reg and not lic_all.empty:
                    lic_reg_col = find_col(lic_all, "fpo", "reg")
                    if lic_reg_col:
                        lic_fpo = lic_all[lic_all[lic_reg_col].astype(str).str.strip() == fpo_reg]
                        if not lic_fpo.empty:
                            st.markdown(section_header("Licenses & Compliance"), unsafe_allow_html=True)
                            lic_status = []
                            for lt in LICENSE_COLS:
                                actual_col = next((c for c in lic_fpo.columns if c.strip() == lt.strip()), None)
                                if actual_col:
                                    val = str(lic_fpo[actual_col].iloc[0]).strip()
                                    clean = val.lower()
                                    status = ("✅ Received" if clean in ["yes", "y", "1", "received"] else 
                                             ("🔄 Applied" if clean in ["applied", "application submitted"] else "❌ Not Applied"))
                                    lic_status.append({"License": lt.strip(), "Status": status, "Value": val})
                            if lic_status:
                                st.dataframe(pd.DataFrame(lic_status), use_container_width=True, hide_index=True)

                # 6. Assessment Parameters
                if fpo_reg and not params_all.empty:
                    params_reg_col = find_col(params_all, "fpo", "reg")
                    if params_reg_col:
                        fpo_params = params_all[params_all[params_reg_col].astype(str).str.strip() == fpo_reg]
                        if not fpo_params.empty:
                            st.markdown(section_header("Assessment Parameters"), unsafe_allow_html=True)
                            score_cols = [c for c in fpo_params.columns if c.startswith("Q") or 
                                         any(k in c.lower() for k in ["score", "profit", "dividend", "turnover"])]
                            if score_cols:
                                st.dataframe(fpo_params[score_cols].head(1), use_container_width=True, hide_index=True)
    else:
        st.info("Performance data not available. Please refresh data.")