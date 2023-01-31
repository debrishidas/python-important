import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from GoogleNews import GoogleNews
from newspaper import Article
from newspaper import Config
from wordcloud import WordCloud, STOPWORDS
import streamlit as st
import logging

nltk.download("vader_lexicon")  # required for Sentiment Analysis
nltk.download("punkt")

logger = logging.getLogger(__name__)


class GOOGLE_NEWS_SENTIMENT_ANALYSIS:
    def __init__(self):
        self.now = dt.date.today().strftime("%m-%d-%Y")
        self.yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime("%m-%d-%Y")

        self.config = Config()
        self.config.browser_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15"
        self.config.request_timeout = 10

    def get_news_url_for_stock(self, stock_symbol):
        # Extract News with Google News
        googlenews = GoogleNews(start=self.yesterday, end=self.now)
        googlenews.search(stock_symbol)
        result = googlenews.result()
        return pd.DataFrame(result)

    def extract_news_keywords(self, stock_symbol, news_url_df):
        try:
            list = []  # creating an empty list
            for i in news_url_df.index:
                dict = (
                    {}
                )  # creating an empty dictionary to append an article in every single iteration
                article = Article(
                    news_url_df["link"][i], config=self.config
                )  # providing the link
                try:
                    article.download()  # downloading the article
                    article.parse()  # parsing the article
                    article.nlp()  # performing natural language processing (nlp)
                except:
                    pass
                # storing results in our empty dictionary
                dict["Date"] = news_url_df["date"][i]
                dict["Media"] = news_url_df["media"][i]
                dict["Title"] = article.title
                dict["Article"] = article.text
                dict["Summary"] = article.summary
                dict["Key_words"] = article.keywords
                list.append(dict)

            check_empty = not any(list)
            # logger.info(check_empty)
            if check_empty == False:
                tokenised_article_df = pd.DataFrame(list)  # creating dataframe
                return tokenised_article_df
        except Exception as e:
            logger.info(
                f"Could not tokenise articles for stock '{stock_symbol}' due to: "
                + str(e)
            )

    # Sentiment Analysis
    def percentage(self, part, whole):
        return 100 * float(part) / float(whole)

    #  Word cloud visualization
    def word_cloud(self, text):
        stopwords = set(STOPWORDS)
        allWords = " ".join([nws for nws in text])
        wordCloud = WordCloud(
            background_color="black",
            width=1600,
            height=800,
            stopwords=stopwords,
            min_font_size=20,
            max_font_size=150,
            colormap="prism",
        ).generate(allWords)
        fig, ax = plt.subplots(figsize=(20, 10), facecolor="k")
        plt.imshow(wordCloud)
        ax.axis("off")
        fig.tight_layout(pad=0)
        st.balloons()
        st.pyplot(fig)

    def sentiment_analysis_plot(self, stock_symbol, tokenised_article_df):

        # Assigning Initial Values
        positive = 0
        negative = 0
        neutral = 0
        # Creating empty lists
        news_list = []
        neutral_list = []
        negative_list = []
        positive_list = []

        # Iterating over the news articles in the dataframe
        for news in tokenised_article_df["Summary"]:
            news_list.append(news)
            analyzer = SentimentIntensityAnalyzer().polarity_scores(news)
            neg = analyzer["neg"]
            neu = analyzer["neu"]
            pos = analyzer["pos"]
            comp = analyzer["compound"]

            if neg > pos:
                negative_list.append(
                    news
                )  # appending the news that satisfies this condition
                negative += 1  # increasing the count by 1
            elif pos > neg:
                positive_list.append(
                    news
                )  # appending the news that satisfies this condition
                positive += 1  # increasing the count by 1
            elif pos == neg:
                neutral_list.append(
                    news
                )  # appending the news that satisfies this condition
                neutral += 1  # increasing the count by 1

        positive = self.percentage(
            positive, len(tokenised_article_df)
        )  # percentage is the function defined above
        negative = self.percentage(negative, len(tokenised_article_df))
        neutral = self.percentage(neutral, len(tokenised_article_df))

        # Converting lists to pandas dataframe
        news_list = pd.DataFrame(news_list)
        neutral_list = pd.DataFrame(neutral_list)
        negative_list = pd.DataFrame(negative_list)
        positive_list = pd.DataFrame(positive_list)

        # Creating PieCart
        labels = [
            "Positive [" + str(round(positive)) + "%]",
            "Neutral [" + str(round(neutral)) + "%]",
            "Negative [" + str(round(negative)) + "%]",
        ]
        sizes = [positive, neutral, negative]
        colors = ["yellowgreen", "blue", "red"]
        fig = plt.figure(figsize=(10, 4))
        plt.pie(sizes, colors=colors, startangle=90)
        plt.style.use("default")
        plt.legend(labels)
        plt.title("Sentiment Analysis Result for stock= " + stock_symbol + "")
        plt.axis("equal")
        st.pyplot(fig)

        logger.info("Wordcloud for " + stock_symbol)
        self.word_cloud(tokenised_article_df["Summary"].values)
