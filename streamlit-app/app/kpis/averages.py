import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


class AVERAGES:
    def rolling_avg(self, input_df):
        input_df["Volume_per_trade"] = input_df["volume"] / input_df["trades"]
        input_df["15SMA"] = input_df["close"].transform(lambda x: x.rolling(15).mean())
        input_df["30SMA"] = input_df["close"].transform(lambda x: x.rolling(30).mean())
        input_df["15SMA_%delivery"] = input_df["%deliverble"].transform(
            lambda x: x.rolling(15).mean()
        )
        input_df["30SMA_%delivery"] = input_df["%deliverble"].transform(
            lambda x: x.rolling(30).mean()
        )
        input_df["15SMA_Volume"] = input_df["volume"].transform(
            lambda x: x.rolling(15).mean()
        )
        input_df["30SMA_Volume"] = input_df["volume"].transform(
            lambda x: x.rolling(30).mean()
        )
        input_df["15SMA_Volume_pertrade"] = input_df["Volume_per_trade"].transform(
            lambda x: x.rolling(15).mean()
        )
        input_df["30SMA_Volume_pertrade"] = input_df["Volume_per_trade"].transform(
            lambda x: x.rolling(30).mean()
        )
        input_df["15SMA_trade"] = input_df["trades"].transform(
            lambda x: x.rolling(15).mean()
        )
        input_df["30SMA_trade"] = input_df["trades"].transform(
            lambda x: x.rolling(30).mean()
        )
        return input_df

    def rolling_diff(self, input_df, col1):
        input_df[col1 + "_diff_%"] = (
            input_df[col1]
            .rolling(window=2)
            .apply(lambda x: (x.iloc[1] - x.iloc[0]) / x.iloc[0])
        )
        return input_df

    def plot_line(self, input_df, arr):
        for x in arr:
            st.line_chart(input_df[x])

    def hist_plot(self, input_df, col):
        fig = plt.figure(figsize=(15, 12))
        sns.distplot(input_df[col], label=col)
        st.pyplot(fig)

    def plot_graph(self, input_df):
        fig = plt.figure(figsize=(15, 12))
        plt.plot(input_df["close"], label="close")
        plt.plot(input_df["close"], label="15SMA")

        st.pyplot(fig)
