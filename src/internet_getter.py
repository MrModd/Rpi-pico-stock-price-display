import re

import secrets
import requests


class RequestException(Exception):
    pass


class InternetGetter:
    @staticmethod
    def get_stock_price(symbol):
        response = requests.get("https://www.alphavantage.co/query?" +
                                "function=GLOBAL_QUOTE" +
                                f"&symbol={symbol}" +
                                "&datatype=json" +
                                f"&apikey={secrets.ALPHAVANTAGE_API_KEY}")
        if response.status_code != 200:
            raise RequestException(f"Returned bad status code: {response.status_code}")

        response_d = response.json()
        print(response_d)
        try:
            price = response_d["Global Quote"]["05. price"]
            change = response_d["Global Quote"]["09. change"]
            change_percent = response_d["Global Quote"]["10. change percent"]
            date = response_d["Global Quote"]["07. latest trading day"]

            # price is in the format xx.xxxx
            price = float(price)
            # change is in the format xx.xxxx
            change = float(change)
            # change_percent is in the format xx.xxxx%
            change_percent = float(change_percent[:-1])

            return (price, change, change_percent, date)
        except KeyError as e:
            raise RequestException(f"Invalid json response, can't find '{e}'")

    @staticmethod
    def get_terminal_stock_price(symbol):
        response = requests.get(f"http://terminal-stocks.dev/{symbol}")
        if response.status_code != 200:
            raise RequestException(f"Returned bad status code: {response.status_code}")

        print(response.text)

        try:
            resp_str = response.text.split("\n")
            stock_info = resp_str[4].split("│")
            date_line = resp_str[6]
            price = re.search("([0-9]+\.[0-9]+)", stock_info[2])
            change = re.search("(-?\$[0-9]+\.[0-9]+)", stock_info[3])
            change_percent = re.search("(-?[0-9]+\.[0-9]+)", stock_info[4])
            # Time is UTC, there's not enough space to print it
            date = re.search("([A-Z][a-z]+ [0-9]+, [0-9]+, [0-9]+:[0-9]+:[0-9]+)", date_line)

            print(f"Price {price.groups()}; " +
                  f"change {change.groups()}; " +
                  f"change percent {change_percent.groups()}; " +
                  f"date {date.groups()}")

            return (float(price.groups()[0]),
                    float(change.groups()[0].replace("$", "")),
                    float(change_percent.groups()[0]),
                    date.groups()[0])
        except Exception as e:
            raise RequestException(f"Cannot parse output: {e}")

    @staticmethod
    def get_current_time(timezone):
        try:
            response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
        except Exception as e:
            print(f"Exception while getting current time: {e}")
            return "N.A."
        if response.status_code != 200:
            # Don't fail just for this
            return "N.A."

        response_d = response.json()
        print(response_d)
        try:
            return response_d["datetime"]
        except KeyError:
            return "N.A."
