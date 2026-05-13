# ══════════════════════════════════════════════════════
# PAGE: LICENSES & COMPLIANCE
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_licenses(fdf):
    """
    Renders the Licenses and Compliance dashboard.
    """
    lic = fdf("license")

    if lic.empty:
        st.info("No license data available for the selected filters.")
        return

    # --- DATA PROCESSING ---
    received = {}
    applied = {}
    not_applied = {}
    total_fpos = len(lic)

    for lt in LICENSE_COLS:
        # Match columns case-insensitively and strip whitespace
        actual_col = next((c for c in lic.columns if c.strip().lower() == lt.strip().lower()), None)
        
        if actual_col is None:
            continue
            
        # Clean the data for counting
        clean = lic[actual_col].astype(str).str.strip().str.lower()
        
        # Categorize statuses
        yes_c  = int(clean.isin(["yes", "y", "1", "received", "done"]).sum())
        app_c  = int(clean.isin(["applied", "application submitted", "in progress"]).sum())
        
        license_name = lt.strip()
        received[license_name]    = yes_c
        applied[license_name]     = app_c
        not_applied[license_name] = int(total_fpos - yes_c - app_c)

    # Create Summary DataFrame
    rec_df = pd.DataFrame({
        "License":     list(received.keys()),
        "Received":    list(received.values()),
        "Applied":     list(applied.values()),
        "Not Applied": list(not_applied.values()),
    }).sort_values("Received", ascending=False)

    # --- KPI SECTION ---
    def safe_kpi(df, idx):
        if len(df) > idx:
            row = df.iloc[idx]
            return (row["License"], f"{row['Received']:,}", f"of {total_fpos} FPOs")
        return ("—", "—", "")

    render_kpis([
        safe_kpi(rec_df, 0), 
        safe_kpi(rec_df, 1), 
        safe_kpi(rec_df, 2), 
        safe_kpi(rec_df, 3)
    ])

    # --- VISUALIZATIONS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(section_header("Received Count by License"), unsafe_allow_html=True)
        fig = px.bar(
            rec_df.sort_values("Received", ascending=True),
            x="Received", y="License", orientation="h",
            template=PLOTLY_TEMPLATE,
            color="Received", 
            color_continuous_scale=["#1B6B3A", "#A5D6A7"],
            text="Received"
        )
        fig.update_traces(textposition='outside')
        fig.update_coloraxes(showscale=False)
        fig.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(section_header("Not Applied Count by License"), unsafe_allow_html=True)
        fig2 = px.bar(
            rec_df.sort_values("Not Applied", ascending=True), # Changed to True for better horizontal bar flow
            x="Not Applied", y="License", orientation="h",
            template=PLOTLY_TEMPLATE,
            color="Not Applied", 
            color_continuous_scale=["#B71C1C", "#FFCDD2"],
            text="Not Applied"
        )
        fig2.update_traces(textposition='outside')
        fig2.update_coloraxes(showscale=False)
        fig2.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # Applied Status Chart
    ap_df = rec_df[rec_df["Applied"] > 0].sort_values("Applied", ascending=False)
    if not ap_df.empty:
        st.markdown(section_header("Applications in Progress (Applied)"), unsafe_allow_html=True)
        fig3 = px.bar(
            ap_df, x="License", y="Applied", 
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[COLORS["amber"]], 
            text="Applied"
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)

    # Stacked Coverage Overview
    st.markdown(section_header("License Coverage (Stacked Overview)"), unsafe_allow_html=True)
    fig4 = px.bar(
        rec_df, x="License", y=["Received", "Applied", "Not Applied"],
        barmode="stack", 
        template=PLOTLY_TEMPLATE,
        color_discrete_map={
            "Received": COLORS["green2"],
            "Applied": COLORS["amber"],
            "Not Applied": COLORS["red"]
        }
    )
    fig4.update_layout(height=400, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig4, use_container_width=True)