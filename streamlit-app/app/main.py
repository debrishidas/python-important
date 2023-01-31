from datetime import date, datetime, timedelta
from utils.webscrapping import MoneyControl, NSE, NSEIndia
from clustering.kmeans import KMEANS
from kpis.averages import AVERAGES
from news_sentiment.google_news_sentiment import GOOGLE_NEWS_SENTIMENT_ANALYSIS
from analysis.technical.analysis import TECHNICAL_ANALYSIS
from analysis.fundamental.analysis import FUNDAMENTAL_ANALYSIS
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import os, sys, pickle
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from streamlit_lottie import st_lottie
import json
import io

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def analysis(product, nse, nseindia, mc, avg1, sentiment_analyser, fa, ta):

    st.title("Fundamental Analysis")
    st.write("Welcome to Fundamental Analysis App")

    mcdir = "./app/pre-processed-files"
    ratiosDF = pd.read_csv(mcdir + "/ratios.csv")
    cashFlowDF = pd.read_csv(mcdir + "/cash_flows.csv")
    balanceSheetDF = pd.read_csv(mcdir + "/balance_sheet.csv")
    incomeStatementDF = pd.read_csv(mcdir + "/annual_is.csv")
    profitLossDF = pd.read_csv(mcdir + "/profit_loss.csv")

    cashFlowDF = cashFlowDF.replace(",", "")
    for k in cashFlowDF.columns[1:-2]:
        cashFlowDF[k] = cashFlowDF[k].str.replace(",", "")
        cashFlowDF[k] = cashFlowDF[k].astype(float)

    selStock = cashFlowDF["stock_name"].unique()[35]


    lottie_finance1 = load_lottiefile("./app/lottiefiles/FINANCE1.json")
    lottie_finance2 = load_lottiefile("./app/lottiefiles/FINANCE2.json")
    lottie_greengraph = load_lottiefile("./app/lottiefiles/GREENGRAPH.json")
    lottie_budgeting = load_lottiefile("./app/lottiefiles/BUDGETING.json")

    Stocks = cashFlowDF["stock_name"].unique()
    Type = ["Fundamental", "Technical", "Quantitative"]
    Analysis = [
        "Balance Sheet",
        "Cash Flow",
        "Income Statement",
        "Projection",
        "DCF",
        "WACC",
        "EBITDA Exit Multiple",
        "Relative Valuation",
        "Financial Ratios",
    ]
    Sheets = ["Balance Sheet", "Cash Flow", "Income Statement"]
    s = st.sidebar.selectbox("Select Stock:", Stocks)
    e = st.sidebar.radio("Analysis Type:", ["Your Own", "Automated"])


    if e == "Your Own":
        c = st.sidebar.radio("Select type of Analysis you want to do:", Type)
        if c == "Fundamental":
            d = st.sidebar.radio("Select Sheet for Analysis:", Sheets)
            if d == "Cash Flow":
                fa.cash_flow_analysis(stock=s)
            elif d == "Balance Sheet":
                fa.balance_sheet_analysis(s)
            else:
                st.title('Income Statement Analysis')
                st.text('Summary of Income...')
                st.text(f'Following Headers are available in a Income Statement: {incomeStatementDF.columns}')
        elif c == "Technical":
            ta.technical_analysis(product, nse, nseindia, mc, avg1, sentiment_analyser)
    else:
        fa.automated_analysis()

def homepage():
    st.title("Welcome to Finshare")
    data_load_state = st.text("Loading data...")
    data_load_state.text("Your one stop place for Stock Analysis..")

    with st.form(key="my_form"):
        username = st.text_input("Username")
        password = st.text_input("Password")
        st.form_submit_button("Login")

    lottie_budgeting = load_lottiefile("./app/lottiefiles/BUDGETING.json")

    st_lottie(
        lottie_budgeting,
        speed=1,
        reverse=False,
        loop=False,
        quality="low",
        height=None,
        width=None,
        key=None,
    )

def streamlit_UI():
    st.session_state.page_select = st.sidebar.selectbox(
                    "Select Page:", ["Homepage","Probe Tool", "Kite Zerodha", "Market News", "Contact"]
                )

    if st.session_state.page_select == 'Homepage':
        homepage()
    elif st.session_state.page_select == 'Probe Tool':
        st.session_state.page_select = 'Probe Tool'
        # Create an object for NSE
        nse = NSE()
        nseindia = NSEIndia()
        mc = MoneyControl()
        avg1 = AVERAGES()
        fa = FUNDAMENTAL_ANALYSIS()
        ta = TECHNICAL_ANALYSIS()

        sentiment_analyser = GOOGLE_NEWS_SENTIMENT_ANALYSIS()
        analysis(st.session_state.page_select, nse, nseindia, mc, avg1, sentiment_analyser, fa, ta)


        # PAGES = {
        #     "FUNDAMENTAL ANALYSIS": FUNDAMENTAL_ANALYSIS().fundamental_analysis,
        #     "TECHNICAL ANALYSIS": TECHNICAL_ANALYSIS().technical_analysis,
        # }

        # analysis_type = st.sidebar.radio("Select one:", list(PAGES.keys()))

        # PAGES[analysis_type](product, nse, nseindia, mc, avg1, sentiment_analyser)




    #     st.markdown(
    #     """
    #     <style>
    #     .reportview-container {
    #         background: url("https://www.investors.com/wp-content/uploads/2020/06/Stock-bearbullchart-02-adobe.jpg")
    #     }
    #     .sidebar .sidebar-content {
    #         background: 'black'
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )

    # Time_Frame_days = 1
    ## Get all NIFTY INDICES

    # Get all urls with sectors

    # Get historic data

    # Get nseIndia symbol List
    # nseindiadf = nseindia.get_symbol_list_from_nseindia()
    # # Select Symbol Name
    # df4 = masterdf.copy()
    # df2 = nseindiadf.copy()
    # df2["company_name"] = df2["name_of_company"].str.contains(company_name_input)
    # company_name = df2[(df2["company_name"] == True)]["symbol"].iloc[0]

    # st.write(mc.test())

    # st.table(mc.get_industry_wise_list([mc.test()[sector_name]])['company_name'])

    # data for the selected stock/derivative
    # st.write(mc.get_industry_wise_list(mc.get_sector_list()[1]))

    # Clustering all stocks using K-mean clustering
    # masterdf = nse.append_symbol_list_data(["symbol", "trades", "deliverable_volume"])
    # Object for Kmeans


if __name__ == "__main__":
    sys.path.append(os.getcwd()+"/app/analysis")
    # print(sys.path)
    streamlit_UI()
