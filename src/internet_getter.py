import secrets
import requests

class InternetGetter:
    @staticmethod
    def get_stock_price(symbol):
        response = requests.get("https://www.alphavantage.co/query?" + \
                                "function=GLOBAL_QUOTE" + \
                                f"&symbol={symbol}" + \
                                "&datatype=json" + \
                                f"&apikey={secrets.ALPHAVANTAGE_API_KEY}")
        if response.status_code != 200:
            return (0.0, 0.0, 0.0, None)

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
        except KeyError:
            return (0.0, 0.0, 0.0, None)

    @staticmethod
    def get_current_time(timezone):
        response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}")
        if response.status_code != 200:
            return ""

        response_d = response.json()
        print(response_d)
        try:
            return response_d["datetime"]
        except KeyError:
            return ""
