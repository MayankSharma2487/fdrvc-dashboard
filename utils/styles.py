import streamlit as st


def load_css():

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    :root {

        --bg: #071018;
        --sidebar: #0B141D;

        --card: rgba(18, 29, 40, 0.78);

        --card-border: rgba(255,255,255,0.06);

        --text: #F4F7FA;

        --muted: #9FB0C0;

        --green: #2ECC71;
        --green2: #27AE60;

        --blue: #3B82F6;

        --purple: #8B5CF6;

        --orange: #F59E0B;

        --shadow:
            0 8px 32px rgba(0,0,0,0.28);
    }

    /* =========================================================
       GLOBAL
    ========================================================= */

    html,
    body,
    .stApp,
    .main,
    .block-container,
    [data-testid="stAppViewContainer"] {

        background:
            radial-gradient(circle at top left, #102235 0%, transparent 35%),
            radial-gradient(circle at top right, #132B20 0%, transparent 30%),
            #071018 !important;

        color: var(--text) !important;

        font-family: 'Inter', sans-serif;
    }

    section.main > div {

        background: transparent !important;

        padding-top: 1rem;
    }

    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="stForm"],
    .element-container {

        background: transparent !important;
    }

    h1,h2,h3,h4,h5,h6 {

        color: white !important;

        font-family: 'Space Grotesk', sans-serif !important;

        font-weight: 700 !important;
    }

    p,
    span,
    label {

        color: var(--text);
    }

    /* =========================================================
       SIDEBAR
    ========================================================= */

    [data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #08111A 0%,
                #0D1722 100%
            ) !important;

        border-right:
            1px solid rgba(255,255,255,0.05);
    }

    [data-testid="stSidebar"] * {

        color: white !important;
    }

/* =========================================================
   PERFECT FILTER FIX
========================================================= */

/* SELECTBOX + MULTISELECT MAIN */

.stSelectbox,
.stMultiSelect {

    background: transparent !important;
}

/* OUTER CONTROL */

.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {

    background: transparent !important;
}

/* ACTUAL INPUT BOX */

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {

    background:
        linear-gradient(
            135deg,
            rgba(15,23,42,0.95),
            rgba(10,18,30,0.95)
        ) !important;

    border:
        1px solid rgba(255,255,255,0.08) !important;

    border-radius: 16px !important;

    color: white !important;

    min-height: 46px !important;

    box-shadow:
        0 4px 14px rgba(0,0,0,0.25);

    transition: all 0.2s ease !important;
}

/* HOVER */

.stSelectbox div[data-baseweb="select"] > div:hover,
.stMultiSelect div[data-baseweb="select"] > div:hover {

    border-color:
        rgba(46,204,113,0.5) !important;

    box-shadow:
        0 0 0 3px rgba(46,204,113,0.08);
}

/* TEXT */

.stSelectbox *,
.stMultiSelect * {

    color: #F8FAFC !important;
}

/* PLACEHOLDER */

.stSelectbox span,
.stMultiSelect span {

    color: #CBD5E1 !important;
}

/* DROPDOWN POPUP */

div[data-baseweb="popover"] {

    background:
        rgba(7,16,24,0.98) !important;

    border:
        1px solid rgba(255,255,255,0.06) !important;

    border-radius: 18px !important;

    overflow: hidden !important;

    backdrop-filter: blur(20px) !important;
}

/* REMOVE WHITE */

div[data-baseweb="popover"] *,
ul[role="listbox"],
li[role="option"] {

    background: transparent !important;

    color: white !important;
}

/* OPTIONS */

li[role="option"] {

    padding: 10px 14px !important;

    border-radius: 10px !important;

    margin: 2px 6px !important;

    transition: 0.15s ease !important;
}

/* OPTION HOVER */

li[role="option"]:hover {

    background:
        rgba(46,204,113,0.14) !important;
}

/* SELECTED OPTION */

li[aria-selected="true"] {

    background:
        rgba(59,130,246,0.22) !important;
}

/* MULTISELECT TAGS */

[data-baseweb="tag"] {

    background:
        linear-gradient(
            135deg,
            rgba(46,204,113,0.18),
            rgba(59,130,246,0.18)
        ) !important;

    border:
        1px solid rgba(46,204,113,0.22) !important;

    border-radius: 10px !important;

    color: white !important;
}

/* SEARCH INPUT */

input {

    background: transparent !important;

    color: white !important;
}

    /* =========================================================
       DROPDOWN MENU FIX
    ========================================================= */

    div[data-baseweb="popover"] {

        background:
            rgba(10,18,28,0.98) !important;

        border:
            1px solid rgba(255,255,255,0.06) !important;

        border-radius: 16px !important;

        backdrop-filter: blur(20px) !important;

        overflow: hidden !important;
    }

    div[data-baseweb="popover"] * {

        background: transparent !important;

        color: white !important;
    }

    ul[role="listbox"] {

        background:
            rgba(10,18,28,0.98) !important;
    }

    li[role="option"] {

        background: transparent !important;

        color: white !important;

        transition: 0.15s ease;

        padding: 10px !important;
    }

    li[role="option"]:hover {

        background:
            rgba(46,204,113,0.12) !important;
    }

    /* selected tags */

    [data-baseweb="tag"] {

        background:
            rgba(46,204,113,0.16) !important;

        border:
            1px solid rgba(46,204,113,0.25) !important;

        border-radius: 10px !important;
    }

    /* =========================================================
       KPI CARDS
    ========================================================= */

    .kpi-card {

        background: var(--card);

        backdrop-filter: blur(18px);

        border:
            1px solid var(--card-border);

        border-radius: 22px;

        padding: 1.2rem 1.3rem;

        min-height: 110px;

        box-shadow: var(--shadow);

        position: relative;

        overflow: hidden;

        transition: 0.25s ease;
    }

    .kpi-card:hover {

        transform:
            translateY(-4px);

        border-color:
            rgba(46,204,113,0.4);
    }

    .kpi-card::before {

        content: "";

        position: absolute;

        top: 0;
        left: 0;

        width: 100%;
        height: 4px;

        background:
            linear-gradient(
                90deg,
                #2ECC71,
                #3B82F6,
                #8B5CF6
            );
    }

    .kpi-label {

        font-size: 0.68rem;

        text-transform: uppercase;

        letter-spacing: 0.12em;

        color: var(--muted);

        font-weight: 700;
    }

    .kpi-value {

        font-size: 2rem;

        color: white;

        font-weight: 800;

        margin-top: 0.35rem;

        font-family: 'Space Grotesk', sans-serif;
    }

    .kpi-sub {

        color: var(--muted);

        font-size: 0.76rem;

        margin-top: 0.35rem;
    }

    /* =========================================================
       SECTION HEADERS
    ========================================================= */

    .section-header {

        font-size: 1.05rem;

        font-weight: 700;

        margin-bottom: 1rem;

        padding-left: 0.85rem;

        border-left: 4px solid #2ECC71;

        font-family: 'Space Grotesk', sans-serif;
    }

    /* =========================================================
       TABS
    ========================================================= */

    .stTabs [data-baseweb="tab-list"] {

        gap: 8px;

        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {

        background:
            rgba(255,255,255,0.04);

        border:
            1px solid rgba(255,255,255,0.06);

        border-radius: 14px !important;

        padding: 10px 18px;

        color: var(--muted) !important;

        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {

        background:
            linear-gradient(
                135deg,
                rgba(46,204,113,0.18),
                rgba(59,130,246,0.18)
            ) !important;

        border-color:
            rgba(46,204,113,0.4) !important;

        color: white !important;
    }

    /* =========================================================
       PLOTLY
    ========================================================= */

    [data-testid="stPlotlyChart"] {

        background:
            rgba(18,29,40,0.72);

        border:
            1px solid rgba(255,255,255,0.05);

        border-radius: 24px;

        padding: 0.8rem;

        backdrop-filter: blur(18px);

        box-shadow: var(--shadow);
    }

    .js-plotly-plot,
    .plotly,
    .plot-container,
    .svg-container {

        background: transparent !important;
    }

    /* =========================================================
       DATAFRAME
    ========================================================= */

    [data-testid="stDataFrame"] {

        background:
            rgba(18,29,40,0.72) !important;

        border-radius: 20px;

        overflow: hidden;

        border:
            1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stDataFrame"] div {

        background: transparent !important;

        color: white !important;
    }

    thead tr th {

        background:
            #12202C !important;

        color: white !important;
    }

    tbody tr td {

        background:
            #0E1822 !important;

        color: white !important;
    }

    /* =========================================================
       BUTTONS
    ========================================================= */

    .stButton button {

        background:
            linear-gradient(
                135deg,
                #2ECC71,
                #27AE60
            ) !important;

        color: white !important;

        border: none !important;

        border-radius: 14px !important;

        font-weight: 700 !important;

        padding: 0.55rem 1.1rem;
    }

    /* =========================================================
       FOOTER
    ========================================================= */

    .footer {

        margin-top: 2rem;

        padding: 1rem;

        text-align: center;

        background:
            rgba(18,29,40,0.72);

        border:
            1px solid rgba(255,255,255,0.05);

        border-radius: 18px;

        color: #A8B7C7;

        font-size: 0.78rem;

        backdrop-filter: blur(18px);
    }

    /* =========================================================
       SCROLLBAR
    ========================================================= */

    ::-webkit-scrollbar {

        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-thumb {

        background: #2ECC71;

        border-radius: 999px;
    }

    </style>
    """, unsafe_allow_html=True)