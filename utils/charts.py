import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import (
    PLOTLY_TEMPLATE,
    COLORS,
    PALETTE
)

# ======================================================
# GLOBAL PLOTLY DARK THEME
# ======================================================

def apply_dark_theme(fig):

    fig.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#EAF2F8",
            family="Inter"
        ),

        title_font=dict(
            color="#FFFFFF",
            size=14
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#EAF2F8")
        ),

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),

        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False
        ),

        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False
        )
    )

    return fig


# ======================================================
# KPI CARD
# ======================================================

def kpi_card(label, value, sub="", clickable=False):

    cls = (
        "kpi-card kpi-clickable"
        if clickable
        else "kpi-card"
    )

    return f"""
    <div class="{cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


# ======================================================
# SECTION HEADER
# ======================================================

def section_header(title):

    return f'''
    <div class="section-header">
        {title}
    </div>
    '''


# ======================================================
# KPI RENDER
# ======================================================

def render_kpis(kpi_list):

    cols = st.columns(len(kpi_list))

    for col, kpi in zip(cols, kpi_list):

        label, val, sub = (
            kpi[0],
            kpi[1],
            kpi[2]
        )

        with col:

            st.markdown(
                kpi_card(label, val, sub),
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)


# ======================================================
# PIE CHART
# ======================================================

def pie_fig(labels, values, title="", colors=None):

    fig = go.Figure(

        go.Pie(

            labels=labels,

            values=values,

            hole=0.5,

            marker=dict(
                colors=colors or PALETTE
            ),

            textinfo="percent+label",

            textfont_size=11
        )
    )

    fig.update_layout(

        title=dict(
            text=title,
            font_size=13
        ),

        template=PLOTLY_TEMPLATE,

        legend=dict(
            orientation="h",
            y=-0.2
        ),

        height=340
    )

    return apply_dark_theme(fig)


# ======================================================
# HORIZONTAL BAR
# ======================================================

def bar_h(
    df_in,
    x_col,
    y_col,
    title="",
    color=None,
    height=400
):

    fig = px.bar(

        df_in,

        x=x_col,

        y=y_col,

        orientation="h",

        title=title,

        template=PLOTLY_TEMPLATE,

        color_discrete_sequence=[
            color or COLORS["green2"]
        ],

        text=x_col
    )

    fig.update_traces(

        texttemplate='%{text:,.1f}',

        textposition='outside'
    )

    fig.update_layout(

        height=height,

        xaxis_title="",

        yaxis_title=""
    )

    return apply_dark_theme(fig)


# ======================================================
# VERTICAL BAR
# ======================================================

def bar_v(
    df_in,
    x_col,
    y_col,
    title="",
    color=None,
    height=360
):

    fig = px.bar(

        df_in,

        x=x_col,

        y=y_col,

        title=title,

        template=PLOTLY_TEMPLATE,

        color_discrete_sequence=[
            color or COLORS["green2"]
        ],

        text=y_col
    )

    fig.update_traces(

        texttemplate='%{text:,.1f}',

        textposition='outside'
    )

    fig.update_layout(

        height=height,

        xaxis_title="",

        yaxis_title=""
    )

    return apply_dark_theme(fig)