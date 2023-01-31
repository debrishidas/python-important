from tracemalloc import start
import pandas as pd
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
from nsepy import get_history
from nsepy.derivatives import get_expiry_date
from urllib import request
import logging
import os, sys, pickle

logger = logging.getLogger(__name__)


class NSE:
    def get_indice_data_from_nse(
        self,
        symbol_name,
        start_date=datetime.today().date(),
        end_date=datetime.today().date(),
        index=True,
    ):
        indice_data = get_history(
            symbol=symbol_name, start=start_date, end=end_date, index=True
        )

        return indice_data

    def get_expiry(ex_year, ex_month):
        try:
            expiry = get_expiry_date(year=ex_year, month=ex_month)
            return list(expiry)[0]
        except Exception as e:
            logger.debug("Error in get_expiry: {}".format(e))
            return None

    def get_futures_data_from_nse(
        self,
        stock_name,
        start_date,
        end_date,
        futures=True,
        expiry_date=get_expiry(
            ex_year=datetime.today().date().year,
            ex_month="{:02d}".format(datetime.today().date().month),
        ),
    ):

        futures = get_history(
            symbol=stock_name,
            start=start_date,
            end=end_date,
            futures=True,
            expiry_date=expiry_date,
        )
        futures.columns = [x.lower().strip().replace(" ", "_") for x in futures.columns]
        return futures

    def get_historic_data_from_nse(
        self,
        stock_name,
        start_date=datetime.today().date(),
        end_date=datetime.today().date(),
    ):
        """Get historic data

        Args:
            stock_name (string): represents stock or derivative
            start_date (date, optional): Start-date to fetch data from. Defaults to datetime.today().date().
            end_date (date, optional): End-date to fetch data to. Defaults to datetime.today().date().

        Returns:
            Dataframe: Pandas dataframe containing historic info
        """

        historic_data = get_history(symbol=stock_name, start=start_date, end=end_date)
        # Change column names
        historic_data.columns = [
            x.lower().strip().replace(" ", "_") for x in historic_data.columns
        ]
        return historic_data

    def append_symbol_list_data(self, col_list_to_select):
        """Append all data for symbol list of NSE

        Args:
            col_list_to_select (list): Columns to select from the raw data

        Returns:
            Dataframe: Containing data for all stocks
        """
        masterdf = pd.DataFrame(columns=col_list_to_select)
        for k in self.stock_symbol_list_nse:
            temp1 = self.get_historic_data_from_nse(k, start_date=date(2022, 1, 1))[:1]
            masterdf = masterdf.append(temp1[col_list_to_select])
        return masterdf


class MoneyControl:
    def __init__(self):
        self.url_for_sector_list = "https://www.moneycontrol.com/india/stockmarket/sector-classification/marketstatistics/nse/automotive.html"
        self.base_url = "https://www.moneycontrol.com"
        self.mc_company_url_dict = {}

    def get_sectors_url_dict(self):
        sectors_url = {}
        sectors_url["Automotive"] = self.url_for_sector_list
        page = requests.get(self.url_for_sector_list)
        html_response = BeautifulSoup(page.content, "html.parser")
        sector_list = html_response.find("div", attrs={"class": "lftmenu"})
        for li in sector_list.find_all("ul")[0].find_all("li"):
            if li.a.get("href") is not None:
                sectors_url[
                    str(li.a.get("href")).split("/")[-1].split(".")[0].title()
                ] = self.base_url + str(li.a.get("href"))
        return sectors_url

    def get_sector_names(self, sector_url_dict):
        return sector_url_dict.keys()

    def get_industry_wise_list(self, sector_url_dict):
        masterdata = []
        headers = []
        for key, url in sector_url_dict.items():
            print(f"Hitting '{url}'.... ")
            try:
                page = requests.get(url, timeout=240)
                soup = BeautifulSoup(page.content, "lxml")
                table = soup.find("table", attrs={"class": "tbldata14 bdrtpg"})
                headers = ["sector_name"] + [
                    [
                        td.get_text(strip=True)
                        if td.get_text(strip=True) is not None
                        else "None"
                        for td in tr.find_all("th")
                    ]
                    for tr in table.find_all("tr")
                ][0]
                data = [
                    [
                        td.get_text(strip=True)
                        if td.get_text(strip=True) is not None
                        else "None"
                        for td in tr.find_all("td")
                    ]
                    for tr in table.find_all("tr")
                ]
                for i in data:
                    if i:
                        i.insert(0, key)
                        masterdata.append(i)
            except Exception as e:
                print(f"Request to '{url}' failed due to { str(e) }")

        # Convert
        print(headers)
        # Initialise masterdf
        masterdf = pd.DataFrame(masterdata, columns=headers)
        # Pre-process column names
        masterdf.columns = [
            x.lower().strip().replace(" ", "_") for x in masterdf.columns
        ]
        # Changing company_name to COMPANYNAME
        # masterdf["company_name"] = [x.upper() for x in masterdf.company_name]
        return masterdf

    def get_company_master_url_dict(self):
        mc_company_base_url = "https://www.moneycontrol.com/india/stockpricequote"

        page = requests.get(mc_company_base_url, timeout=240)
        soup = BeautifulSoup(page.content, "lxml")
        div = soup.find("div", attrs={"class": "MT2 PA10 brdb4px alph_pagn"})

        for a in div.find_all("a", href=True):
            base_url = "https://www.moneycontrol.com" + a["href"]
            print(f"Hitting {base_url}")

            subpage = requests.get(base_url, timeout=240)
            subsoup = BeautifulSoup(subpage.content, "lxml")
            table = subsoup.find("table", attrs={"class": "pcq_tbl MT10"})

            for tr in table.find_all("tr"):
                for td in tr.find_all("td"):
                    company_name = td.get_text().upper().strip()
                    # print(company_name)
                    url = td.a.get("href")
                    self.mc_company_url_dict[company_name] = url
        return self.mc_company_url_dict

    def get_overview_data_for_a_stock(self, mc_company_url):
        page = requests.get(mc_company_url, timeout=240)
        soup = BeautifulSoup(page.content, "lxml")
        nseview = soup.find_all(
            "div", attrs={"class": "nsestock_overview bsestock_overview"}
        )

        data = []
        for nsediv in nseview:
            tables = nsediv.find_all("div", attrs={"class": "oview_table"})
            for table in tables:
                data = data + [
                    [
                        td.get_text(strip=True)
                        if td.get_text(strip=True) is not None
                        else "None"
                        for td in tr.find_all("td")
                    ]
                    for tr in table.find_all("tr")
                ]
        # metricdf = pd.DataFrame(data)
        # metric_transpose_df = metricdf.transpose()
        # headers = metric_transpose_df.iloc[0]
        # # print(headers)
        # metric_transpose_df = metric_transpose_df[1:]
        # metric_transpose_df.columns = headers
        # metric_transpose_df.columns = [
        #     x.strip().replace("[#,@,&]();", "") for x in metric_transpose_df.columns
        # ]
        return data

    def get_detailedfinancial_quicklinks_dict(self, mc_company_url):
        quicklinks_dict = {}
        page = requests.get(mc_company_url, timeout=240)
        soup = BeautifulSoup(page.content, "lxml")
        quicklinks = soup.find_all("div", attrs={"class": "quick_links clearfix"})
        for li in quicklinks[0].find_all("ul")[0].find_all("li"):
            if li.a.get("href") is not None:
                quicklinks_dict[str(li.a.get("title")).strip()] = str(li.a.get("href"))
        return quicklinks_dict

    def get_detailed_fundamental_df(self, url):
        page = requests.get(url, timeout=240)
        soup = BeautifulSoup(page.content, "lxml")
        tables = soup.find_all("table", attrs={"class": "mctable1"})
        for table in tables:
            data = [
                [
                    td.get_text(strip=True)
                    if td.get_text(strip=True) is not None
                    else "None"
                    for td in tr.find_all("td")
                ]
                for tr in table.find_all("tr")
            ]
        metricdf = pd.DataFrame(data)
        metric_transpose_df = metricdf.transpose()
        headers = metric_transpose_df.iloc[0]
        # print(headers)
        metric_transpose_df = metric_transpose_df[1:]
        metric_transpose_df.columns = headers
        metric_transpose_df.columns = [
            x.strip().replace("[#,@,&]();", "").lower()
            for x in metric_transpose_df.columns
        ]
        metric_transpose_df.dropna(axis=1, how="all", inplace=True)
        return metric_transpose_df


class NSEIndia:
    def get_symbol_list_from_nseindia(self):
        # Retrieve the webpage as a string
        response = request.urlopen(
            "https://www1.nseindia.com/content/equities/EQUITY_L.csv"
        )
        csv = response.read()
        # Save the string to a file
        csvstr = str(csv).strip("b'")
        lines = csvstr.split("\\n")
        data = []
        for line in lines:
            data.append(line.replace('"', "").split(","))

        headers = data[0]
        data.pop(0)
        # convert into pandas dataframe
        df = pd.DataFrame(data, columns=headers)
        # Pre-process column names
        df.columns = [x.lower().strip().replace(" ", "_") for x in df.columns]
        return df
