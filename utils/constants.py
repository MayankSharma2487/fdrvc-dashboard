# utils/constants.py

# ─────────────────────────────────────────────
# REPORT URLS
# ─────────────────────────────────────────────

REPORT_URLS = {

    "registration":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=New_FPO_Registration_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "shareholder":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPO_shareholder_bod_report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "crop":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPO_Crop_Detail_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "overall_turnover":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPO_Overall_Turnover_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "yearwise_turnover":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPO_Yearwise_Turnover_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "license":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPO_License_Onboarding_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "staff":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPO_Staff_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "performance":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPOwise_Performace_Report.rptdesign&ia_id=1&ministry=null&npma=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "training":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=Training_and_Exposure_Visit_report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "management_cost":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=fpo_management_cost.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "equity":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=equity_grant.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "credit":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=Credit_Availed_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "base":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=Base_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "profile":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=New_FPO_Profile_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "parameters":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=FPOAssessmentParametersReport.rptdesign&ia_id=1&cbbo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "cbbo_cost":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=CBBOMilestoneCostReport.rptdesign&ia_id=1&cbbo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "score":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=Draft_fpo_parameter_scorecard_IA_2024_2025.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",

    "domain_expert":
    "https://10kfpomis.dac.gov.in/birt/frameset?__report=CBBO_Domain_Expert_Report.rptdesign&ia_id=1&cbbo_id=null&fpo_id=null&npma=null&ministry=null&__ExcelEmitter.SingleSheet=true&__ExcelEmitter.SingleSheetWithPageBreaks=true&__ExcelEmitter.DisableGrouping=true&__dpi=96&__format=xlsx&__asattachment=true&__overwrite=false",
}

# ─────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────

CACHE_DURATION_HOURS = 6

# ─────────────────────────────────────────────
# FILE SAVE PATHS
# ─────────────────────────────────────────────

SAVE_PATH = "saved_cbbo_cost.xlsx"

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────

PLOTLY_TEMPLATE = dict(

    layout=dict(

        paper_bgcolor="#111915",

        plot_bgcolor="#111915",

        font=dict(
            color="#C8DFC8",
            family="Plus Jakarta Sans"
        ),

        colorway=[
            "#2E9E5B",
            "#F5A623",
            "#1A6FBF",
            "#E04545",
            "#7B3FA0",
            "#00A896",
            "#F57C00"
        ],

        xaxis=dict(
            gridcolor="#1E2B1F",
            linecolor="#1E2B1F"
        ),

        yaxis=dict(
            gridcolor="#1E2B1F",
            linecolor="#1E2B1F"
        ),

        legend=dict(
            bgcolor="#182118",
            bordercolor="#253025"
        ),

        margin=dict(
            l=40,
            r=20,
            t=40,
            b=40
        ),
    )
)

# ─────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────

COLORS = {

    "green": "#1B6B3A",
    "green2": "#2E9E5B",

    "amber": "#F5A623",

    "red": "#E04545",

    "blue": "#1A6FBF",

    "teal": "#00A896",

    "purple": "#7B3FA0",

    "orange": "#F57C00",

    "pink": "#E84393",
}

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────

PALETTE = [

    "#2E9E5B",   # green
    "#F5A623",   # amber
    "#1A6FBF",   # blue
    "#E04545",   # red
    "#7B3FA0",   # purple
    "#00A896",   # teal
    "#F57C00",   # orange
    "#E84393",   # pink
]
# ─────────────────────────────────────────────
# LICENSE COLUMNS
# ─────────────────────────────────────────────

LICENSE_COLS = [

    "Seed License",

    "Fertilizer License ",

    "Pesticide License ",

    "Mandi License ",

    "FSSAI License",

    "GST",

    "Business Certificate",

    "CSC",

    "Onboarded on ONDC",

    "Onboarded on e-NAM",

    "Onboarded on GeM",

    "Reg. with Apeda"
]

# ─────────────────────────────────────────────
# MANAGEMENT COST MAP
# ─────────────────────────────────────────────

MC_INSTALLMENT_MAP = {

    "1st Installment": "1st Installment",

    "2 nd Installment": "2 nd Installment",

    "3rd Installment": "3rd Installment",

    "4th Installment": "4th Installment",

    "5th Installment": "5th Installment",

    "6th Installment": "6th Installment",
}

# ─────────────────────────────────────────────
# CBBO MILESTONE COST MAP
# ─────────────────────────────────────────────

CBBO_MILESTONE_COST_MAP = {

    "1": 0.18,

    "2": 0.09,

    "3": 0.06,

    "4": 0.03
}