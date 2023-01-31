from datetime import date, datetime, timedelta
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
from clustering.kmeans import KMEANS

class TECHNICAL_ANALYSIS:
    def technical_analysis(self, product, nse, nseindia, mc, avg1, sentiment_analyser):
        st.title("Technical Analysis")
        st.write("Welcome to Technical Analysis App")

        files_dir = "app/files/"
        nse_all = pd.read_csv(files_dir + "nse_nifty_all_stocks.csv")
        nse_indices = pd.read_csv(files_dir + "nse_all_indices.csv")

        INDICE_OR_STOCK = st.sidebar.radio("Select one:", ["NIFTY INDICES", "NIFTY STOCKS"])

        days_months_dict = {
            1: 30,
            3: 90,
            6: 180,
            9: 270,
            12: 360,
            15: 450,
            18: 540,
            24: 720,
        }

        if INDICE_OR_STOCK == "NIFTY INDICES":

            INDICE_OR_FUT = st.sidebar.radio("Select one:", ["INDEX", "FUTURES"])
            indices_name = st.sidebar.selectbox(
                "NIFTY INDICE", nse_indices.INDEX.unique()[:10]
            )
            st.title(f"{indices_name}-Charts")
            Time_Frame_days = st.sidebar.selectbox(
                "Select Time Frame (in Months)", np.sort([1, 3, 6, 9, 12, 15, 18, 24])[::-1]
            )
            if INDICE_OR_FUT == "INDEX":
                indice_df = nse.get_indice_data_from_nse(
                    indices_name,
                    start_date=datetime.today().date()
                    - timedelta(days=days_months_dict[Time_Frame_days]),
                )
                st.line_chart((indice_df["Close"]))
                indice_df = avg1.rolling_diff(indice_df, "Close")
                st.line_chart((indice_df["Close_diff_%"]))
                avg1.hist_plot(indice_df, "Close_diff_%")
                st.write(f"Mean = {round(indice_df['Close_diff_%'].mean(),4)}")
                st.write(f"Std = {round(indice_df['Close_diff_%'].std(),4)}")
                st.write(
                    f"Std/Mean = {round(indice_df['Close_diff_%'].std()/indice_df['Close_diff_%'].mean(),4)}"
                )

            else:
                st.write("Coming soon..")
        else:
            # Read from pickle files
            with open(f"{os.getcwd()}/app/files/sector_url_dict.pickle", "rb") as f:
                sector_url_dict = pickle.load(f)

            sector_name = st.sidebar.selectbox("Sector", list(sector_url_dict.keys()))

            # Input sub-sectors
            all_stocks_industry_wise_df = pd.read_csv(
                f"{os.getcwd()}/app/files/all_stocks_industry_wise_df.csv", header=0
            )
            sub_sector_names = all_stocks_industry_wise_df[
                (all_stocks_industry_wise_df["sector_name"] == sector_name)
            ]["industry"].unique()

            sub_sector_name = st.sidebar.selectbox("Sub-sector", sub_sector_names)

            # Input company name
            company_names = all_stocks_industry_wise_df[
                (all_stocks_industry_wise_df["industry"] == sub_sector_name)
            ]["company_name"].unique()
            company_name = st.sidebar.selectbox("Company", np.sort(company_names))

            Time_Frame_days = st.sidebar.selectbox(
                "Select Time Frame (in Months)", np.sort([1, 3, 6, 9, 12, 15, 18, 24])[::-1]
            )
            Equity_Futures_Options = st.sidebar.radio(
                "Select one:", ["Equity", "Futures", "Options"]
            )

            st.title(f"{company_name}-Charts")
            if st.button(
                label="News Sentiment",
                help=f"Look at what is in the news for {company_name}",
            ):
                # Extract news for stock
                news_url_df = sentiment_analyser.get_news_url_for_stock(company_name)
                # Extract the keywords from the news
                tokenised_article_df = sentiment_analyser.extract_news_keywords(
                    company_name, news_url_df
                )
                sentiment_analyser.sentiment_analysis_plot(
                    company_name, tokenised_article_df
                )

                st.write("Have a look at the Top 5 news for the company")
                st.table(news_url_df.head(5)["link"].values.tolist())

            st.title("Overview")
            # Get master_company_url_dict_from moneycontrol
            with open(f"{os.getcwd()}/app/files/company_url_dict.pickle", "rb") as handle:
                mc_master_company_url_dict = pickle.load(file=handle)

            company_url = mc_master_company_url_dict[company_name.upper()]
            overviewdata = mc.get_overview_data_for_a_stock(company_url)

            # Display metric format
            no_cols = 4
            no_rows = int(len(overviewdata) / no_cols)
            for i in range(1, no_rows):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(
                    label=overviewdata[(i * no_rows) - 4][0],
                    value=overviewdata[(i * no_rows) - 4][1],
                )
                col2.metric(
                    label=overviewdata[(i * no_rows) - 3][0],
                    value=overviewdata[(i * no_rows) - 3][1],
                )
                col3.metric(
                    label=overviewdata[(i * no_rows) - 2][0],
                    value=overviewdata[(i * no_rows) - 2][1],
                )
                col4.metric(
                    label=overviewdata[(i * no_rows) - 1][0],
                    value=overviewdata[(i * no_rows) - 1][1],
                )
                st.write(" ")

            if Equity_Futures_Options == "Equity":
                historic_df = nse.get_historic_data_from_nse(
                    company_name,
                    start_date=datetime.today().date()
                    - timedelta(days=days_months_dict[Time_Frame_days]),
                )
                historic_df = avg1.rolling_avg(historic_df)
                historic_df = avg1.rolling_diff(historic_df, "close")
                avg1.hist_plot(historic_df, "close_diff_%")
                avg1.plot_line(
                    historic_df,
                    [
                        "close",
                        "15SMA",
                        "30SMA",
                        "close_diff_%",
                        "%deliverble",
                        "15SMA_%delivery",
                        "30SMA_%delivery",
                        "volume",
                        "15SMA_Volume",
                        "30SMA_Volume",
                        "trades",
                        "15SMA_trade",
                        "30SMA_trade",
                        "Volume_per_trade",
                        "15SMA_Volume_pertrade",
                        "30SMA_Volume_pertrade",
                    ],
                )
                kmeans = KMEANS()
                fig = kmeans.k_means_cluster(4, historic_df, "volume", "%deliverble")
                st.pyplot(fig)
            # elif Equity_Futures_Options == "Futures":
            #     futures_df = nse.get_futures_data_from_nse(
            #         company_name,
            #         start_date=datetime.today().date()
            #         - timedelta(days=days_months_dict[Time_Frame_days]),
            #     )
            #     st.write(futures_df)
            #     avg1.plot_line(
            #         futures_df,
            #         [
            #             "last",
            #             "settle_price",
            #             "open_interest",
            #             "change_in_oi",
            #             "number_of_contracts",
            #         ],
            #     )
            else:
                st.write("Options Data coming soon..")
