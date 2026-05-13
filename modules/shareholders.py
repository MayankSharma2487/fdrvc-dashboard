# ══════════════════════════════════════════════════════
# PAGE: SHAREHOLDERS
# ══════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import *
from utils.charts import *
from utils.constants import *
from utils.filters import *

def show_shareholders(fdf):
    """
    Renders the Shareholders demographic and distribution dashboard.
    """
    profile = fdf("profile")
    base    = fdf("base")

    if profile.empty and base.empty:
        st.info("No shareholder data available for the current filters.")
        return

    # --- DATA CALCULATION ---
    total_sh = int(safe_sum(profile, "Total Shareholders")) if not profile.empty else 0
    women_sh = int(safe_sum(profile, "No. of women shareholders")) if not profile.empty else 0
    men_sh   = int(safe_sum(profile, "No. of men shareholders"))   if not profile.empty else 0
    sc_sh    = int(safe_sum(profile, "No of Scheduled Caste (SC) shareholders")) if not profile.empty else 0
    st_sh    = int(safe_sum(profile, "No of Scheduled Tribe (ST) shareholders")) if not profile.empty else 0

    # Safety check for percentages
    denom = max(total_sh, 1)
    
    # --- KPI SECTION ---
    render_kpis([
        ("Total Shareholders", f"{total_sh:,}", "Farmer members"),
        ("Women Shareholders", f"{women_sh:,}", f"{(women_sh / denom * 100):.1f}% of total"),
        ("Men Shareholders",   f"{men_sh:,}",   f"{(men_sh / denom * 100):.1f}% of total"),
        ("SC Shareholders",    f"{sc_sh:,}",    "Scheduled Caste"),
        ("ST Shareholders",    f"{st_sh:,}",    "Scheduled Tribe"),
    ])

    # --- TOP ROW: SOCIAL & GENDER ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(section_header("Social Category Distribution"), unsafe_allow_html=True)
        if not profile.empty:
            cat_data = {
                "General": int(safe_sum(profile, "No of General shareholders")),
                "OBC":     int(safe_sum(profile, "No of Other Backward Classes(OBC) shareholders")),
                "SC":      sc_sh, 
                "ST":      st_sh,
                "Others":  int(safe_sum(profile, "No of Others shareholders")),
            }
            cat_df = pd.DataFrame({"Category": list(cat_data.keys()), "Count": list(cat_data.values())})
            cat_df = cat_df[cat_df["Count"] > 0]
            
            if not cat_df.empty:
                st.plotly_chart(pie_fig(
                    cat_df["Category"], 
                    cat_df["Count"], 
                    "Social Categories",
                    colors=[COLORS["blue"], COLORS["amber"], COLORS["red"], COLORS["green2"], COLORS["purple"]]
                ), use_container_width=True)
            else:
                st.info("Social category data points are zero or missing.")

    with c2:
        st.markdown(section_header("Gender Distribution"), unsafe_allow_html=True)
        if not profile.empty:
            other_gen = int(safe_sum(profile, "No. of other shareholders"))
            gdf = pd.DataFrame({
                "Gender": ["Men", "Women", "Other"],
                "Count": [men_sh, women_sh, other_gen]
            })
            gdf = gdf[gdf["Count"] > 0]
            
            if not gdf.empty:
                st.plotly_chart(pie_fig(
                    gdf["Gender"], 
                    gdf["Count"], 
                    "Gender Split",
                    colors=[COLORS["blue"], COLORS["red"], COLORS["amber"]]
                ), use_container_width=True)
            else:
                st.info("Gender data points are zero or missing.")

    # --- BOTTOM ROW: LANDHOLDING & GEOGRAPHY ---
    c3, c4 = st.columns(2)
    
    with c3:
        st.markdown(section_header("Landholding Categories"), unsafe_allow_html=True)
        if not profile.empty:
            land_cols = {
                "Small": "Small Farmers ", 
                "Marginal": "Marginal Farmer", 
                "Landless": "Landless Farmer",
                "Tenant": "Tenant Farmer", 
                "Large": "Large Farmer", 
                "Other": "Other Farmer"
            }
            land_data = {cat: int(safe_sum(profile, col)) for cat, col in land_cols.items()}
            land_df = pd.DataFrame({"Category": list(land_data.keys()), "Count": list(land_data.values())})
            land_df = land_df[land_df["Count"] > 0]
            
            if not land_df.empty:
                st.plotly_chart(pie_fig(land_df["Category"], land_df["Count"], "Landholding"), use_container_width=True)
            else:
                st.info("Landholding details not available.")

    with c4:
        st.markdown(section_header("Shareholders State-Wise"), unsafe_allow_html=True)
        if not base.empty:
            state_col = find_col(base, "state", "name")
            sh_col    = find_col(base, "total", "shareholder")
            
            if state_col and sh_col:
                sv = base.groupby(state_col)[sh_col].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).reset_index()
                sv.columns = ["State", "Shareholders"]
                sv = sv[sv["Shareholders"] > 0].sort_values("Shareholders", ascending=False).head(15)
                
                if not sv.empty:
                    st.plotly_chart(bar_v(sv, "State", "Shareholders", "", COLORS["teal"]), use_container_width=True)
                else:
                    st.info("No active shareholders found in base data.")
            else:
                st.warning("Missing required columns: State or Total Shareholder.")