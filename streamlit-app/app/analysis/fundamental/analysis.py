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
from analysis.technical.analysis import TECHNICAL_ANALYSIS
from streamlit_lottie import st_lottie


def balanceSheetF1(stock):
    mcdir = './app/pre-processed-files'
    balanceSheetDF = pd.read_csv(mcdir + '/balance_sheet.csv')

    cond = balanceSheetDF["stock_name"] == stock
    test = balanceSheetDF[cond]
    # test = test.fillna(0)
    #test = test.sort_values(by=['month-year'],ascending=True)

    for k in test.columns[1:-1]:
        test[k] = test[k].astype(str)
        test[k] = test[k].str.replace(',','')
        test[k] = test[k].str.replace('--','0')
        test[k] = test[k].astype(float)
    return(test)


class FUNDAMENTAL_ANALYSIS:

    def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

    def automated_analysis(self):
        lottie_finance2 = FUNDAMENTAL_ANALYSIS.load_lottiefile("./app/lottiefiles/FINANCE2.json")
        st.title("Automated Analysis: Well Curated steps for your understanding ")
        st_lottie(
            lottie_finance2,
            speed=1,
            reverse=False,
            loop=False,
            quality="low",
            height=None,
            width=None,
            key=None,
        )
        df1 = pd.read_excel("dabur_valuation.xlsx", engine="openpyxl")

        df1 = df1[
            [
                "Ratio",
                "Type",
                "03/31/2007",
                "03/31/2008",
                "03/31/2009",
                "03/31/2010",
                "03/31/2011",
                "03/31/2012",
                "03/31/2013",
                "03/31/2014",
                "03/31/2015",
                "03/31/2016",
                "03/31/2017",
                "03/31/2018",
                "03/31/2019",
                "03/31/2020",
                "03/31/2021",
            ]
        ]

        val_vars = [
            "03/31/2007",
            "03/31/2008",
            "03/31/2009",
            "03/31/2010",
            "03/31/2011",
            "03/31/2012",
            "03/31/2013",
            "03/31/2014",
            "03/31/2015",
            "03/31/2016",
            "03/31/2017",
            "03/31/2018",
            "03/31/2019",
            "03/31/2020",
            "03/31/2021",
        ]

        id_vars = ["Ratio"]

        growth_ratios = [
            "Growth%|EBITDA Margin",
            "Growth%|Effective Tax Rate",
            "Growth%|Income before XO Margin",
            "Growth%|Incremental Operating Margin",
            "Growth%|Net Income Margin",
            "Growth%|Net Income to Common Margin",
            "Growth%|Operating Margin",
            "Growth%|Pretax Margin",
            "Growth%|Return on Assets",
            "Growth%|Return on Capital",
            "Growth%|Return on Common Equity",
            "Growth%|Return on Invested Capital",
            "Growth%|Sustainable Growth Rate",
        ]

        df1T = pd.melt(df1, id_vars=id_vars, value_vars=val_vars).sort_values(
            by=["Ratio", "variable"], ascending=[True, True]
        )
        df1T = df1T.rename(
            columns={"Ratio": "RatioType", "variable": "Year", "value": "Ratio"}
        )
        df1TG = df1T.groupby("RatioType")
        df1T["diff"] = df1TG.Ratio.diff()
        df1T["Growth%"] = df1T["diff"] * 100 / df1T["Ratio"].shift(1)

        df1TP = df1T.pivot(
            index="Year", columns="RatioType", values=["Ratio", "diff", "Growth%"]
        ).reset_index()
        df1TP.columns = df1TP.columns.map("|".join).str.strip("|")

        data = df1TP
        # Notify the reader that the data was successfully loaded.

        st.image("./Images/Dabur_Logo.png", width=200)
        st.title("Dabur Stock Valuation Study")
        b = st.sidebar.radio("Choose Automated Analysis:", Analysis)
        if b == "Financial Ratios":
            a = st.sidebar.multiselect(
                "Select a Financial Ratio for analysis:", df1T["RatioType"].unique()
            )

            ratio_arr = ["Year"]
            growth_arr = ["Year"]

            for q in a:
                ratio_search = f"Ratio|{q}"
                growth_search = f"Growth%|{q}"
                ratio_arr.append(ratio_search)
                growth_arr.append(growth_search)

                fig1 = px.line(
                    df1TP,
                    x="Year",
                    y=df1TP[ratio_arr].columns[1:],
                    title=f"Ratios Over Time",
                    width=1000,
                    height=600,
                    markers=True,
                )
                fig1.update_layout(
                    paper_bgcolor="#000000",
                )
                st.plotly_chart(fig1)

                # st.table(df1TP[growth_arr])
                fig2 = px.line(
                    df1TP,
                    x="Year",
                    y=df1TP[growth_arr].columns[1:],
                    title=f"Growth Over Time",
                    width=1000,
                    height=600,
                    markers=True,
                )
                fig2.update_layout(
                    paper_bgcolor="#000000",
                )

                st.plotly_chart(fig2)

                df1TPCorr = df1TP[growth_arr].corr()

                x = list(df1TPCorr.columns)
                y = list(df1TPCorr.index)
                z = np.array(df1TPCorr)

                try:
                    fig = ff.create_annotated_heatmap(
                        z,
                        x=x,
                        y=y,
                        annotation_text=np.around(z, decimals=2),
                        hoverinfo="z",
                        colorscale="Viridis",
                    )

                    fig.update_layout(
                        autosize=False,
                        width=1100,
                        height=800,
                    )

                    st.plotly_chart(fig)
                except:
                    st.write("Please enter 1 ratio to get the correlation heatmap")

                csv = convert_df(df1TP[ratio_arr])
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name="test_df.csv",
                    mime="text/csv",
                )
        d = st.sidebar.checkbox("Master Dashboard")

    def cashflowF1(stock, cashFlowDF):
        st.title("Cash Flow Analysis")
        cond = cashFlowDF["stock_name"] == stock
        test = cashFlowDF[cond]
        # test['Summation']  = test['net cashflow from operating activities'] + \
        # test['net cash used in investing activities'] + \
        # test['net cash used from financing activities'] + \
        # test['adjustments on amalgamation merger demerger others'] + \
        # test['foreign exchange gains / losses'] ## equivalent to net inc/dec in cash and cash equivalents
        # test = test.sort_values(by=['month-year'],ascending=True)
        test["Delta Operating"] = test["net cashflow from operating activities"].diff()
        test["Delta Investing"] = test["net cash used in investing activities"].diff()
        test["Delta Financing"] = test["net cash used from financing activities"].diff()
        test["Growth% Operating"] = (
            test["Delta Operating"]
            * 100
            / test["net cashflow from operating activities"].shift(1)
        )
        test["Growth% Investing"] = (
            test["Delta Investing"]
            * 100
            / test["net cash used in investing activities"].shift(1)
        )
        test["Growth% Financing"] = (
            test["Delta Financing"]
            * 100
            / test["net cash used from financing activities"].shift(1)
        )
        return test


    def balance_sheet_analysis(self, s):

        mcdir = './app/pre-processed-files'
        balanceSheetDF = pd.read_csv(mcdir + '/balance_sheet.csv')

        st.title('Balance Sheet Analysis')
        st.text('Summary of financial balances...')

        st.text(f'Following Headers are available in a Balance Sheet: {balanceSheetDF.columns}')
        plottype = st.radio('Select type of plot:', ['line', 'bar'])
        # st.text('Summary of financial balances...')
        cols2 = ['total share capital', 'total reserves and surplus','total shareholders funds']
        if plottype == 'bar':
            fig3 = px.bar(balanceSheetF1(s), x="month-year", y=cols2, title=f'Shareholders Fund {s} Over Time',width=800, height=500)
        else: fig3 = px.line(balanceSheetF1(s), x="month-year", y=cols2, title=f'Shareholders Fund {s} Over Time',width=800, height=500,markers=True)
        fig3.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig3,use_container_width = True)

        # st.text('Summary of financial balances...')
        #plottype1 = st.radio('Select type of plot:', ['Line', 'bar'])
        cols3 = ['short term borrowings', 'trade payables','other current liabilities','short term provisions','total current liabilities']
        if plottype == 'bar':
                    fig4 = px.bar(balanceSheetF1(s), x="month-year", y=cols3, title=f'Current Liability of {s} Over Time',width=800, height=500)
        else : fig4 = px.line(balanceSheetF1(s), x="month-year", y=cols3, title=f'Current Liability of {s} Over Time',width=800, height=500)
        fig4.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig4,use_container_width = True)

        # st.text('Summary of financial balances...')
        #plottype2 = st.radio('Select type of plot:', ['line', 'bar'])
        cols4 = ['long term borrowings', 'deferred tax liabilities [net]','other long term liabilities',
'long term provisions','total non-current liabilities']
        if plottype == 'bar':
                    fig5 = px.bar(balanceSheetF1(s), x="month-year", y=cols4, title=f'Non-Current Liability Fund of {s} Over Time',width=800, height=500)
        else: fig5 = px.line(balanceSheetF1(s), x="month-year", y=cols4, title=f'Non-Current Liability Fund of {s} Over Time',width=800, height=500)
        fig5.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig5,use_container_width = True)
        #plottype3 = st.radio('Select type of plot:', ['line', 'bar'])
        cols5 = ['total assets','total non-current assets','total current assets']
        if plottype == 'bar':
                    fig6 = px.bar(balanceSheetF1(s), x="month-year", y=cols5, title=f'Total Assets of {s} Over Time',width=800, height=500)
        else : fig6 = px.line(balanceSheetF1(s), x="month-year", y=cols5, title=f'Total Assets of {s} Over Time',width=800, height=500)
        fig6.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig6,use_container_width = True)

        cols6 = ['tangible assets','intangible assets','capital work-in-progress','other assets','fixed assets']
        if plottype == 'bar':
                    fig7 = px.bar(balanceSheetF1(s), x="month-year", y=cols6, title=f'Fixed Assets of {s} Over Time',width=800, height=500)
        else : fig7 = px.line(balanceSheetF1(s), x="month-year", y=cols6, title=f'Fixed Assets of {s} Over Time',width=800, height=500)
        fig7.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig7,use_container_width = True)

        cols7 = ['fixed assets','non-current investments','deferred tax assets [net]','long term loans and advances','other non-current assets']
        if plottype == 'bar':
                    fig8 = px.bar(balanceSheetF1(s), x="month-year", y=cols7, title=f'Non-Current  Assets of {s} Over Time',width=800, height=500)
        else : fig8 = px.line(balanceSheetF1(s), x="month-year", y=cols7, title=f'Non-Current Assets of {s} Over Time',width=800, height=500)
        fig8.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig8,use_container_width = True)

    def cash_flow_analysis(self, stock):
        mcdir = './app/pre-processed-files'
        cashFlowDF = pd.read_csv(mcdir + '/cash_flows.csv')

        for k in cashFlowDF.columns[1:-2]:
            cashFlowDF[k] = cashFlowDF[k].str.replace(',','')
            cashFlowDF[k] = cashFlowDF[k].astype(float)

        selStock = cashFlowDF['stock_name'].unique()[35]

        st.title("Cash Flow Analysis")
        st.text("Summary of Cash Movement...")
        st.text(
            f"Following Headers are available in a Cash Flow Statement: {cashFlowDF.columns}"
        )
        cols = [
            "net cashflow from operating activities",
            "net cash used in investing activities",
            "net cash used from financing activities",
        ]
        fig2 = px.bar(
            FUNDAMENTAL_ANALYSIS.cashflowF1(stock, cashFlowDF),
            x="month-year",
            y=cols,
            title=f"Cash Flow of {stock} Over Time",
            width=800,
            height=500,
        )
        fig2.update_layout(
            paper_bgcolor="#000000",
        )
        st.plotly_chart(fig2, use_container_width=True)
