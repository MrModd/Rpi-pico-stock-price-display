import secrets

class InternetGetter:
    STOCK_API_URL = "https://www.alphavantage.co/query?" + \
            "function=GLOBAL_QUOTE" + \
            f"&symbol=ARM" + \
            "&datatype=json" + \
            f"&apikey={secrets.ALPHAVANTAGE_API_KEY}"
    TIME_API_URL = "http://worldtimeapi.org/api/timezone/Europe/Paris"

    @staticmethod
    def get_stock_price(connection):
        response_d = connection.request_json(InternetGetter.STOCK_API_URL)
        print(response_d)
        try:
            price = response_d["Global Quote"]["05. price"]
            change = response_d["Global Quote"]["09. change"]
            change_percent = response_d["Global Quote"]["10. change percent"]
            last_day = response_d["Global Quote"]["07. latest trading day"]

            # price is in the format xx.xxxx
            price = float(price)
            # change is in the format xx.xxxx
            change = float(change)
            # change_percent is in the format xx.xxxx%
            change_percent = float(change_percent[:-1])

            return (price, change, change_percent, last_day)
        except KeyError:
            return (0.0, 0.0, 0.0, None)

    @staticmethod
    def get_current_time(connection):
        response_d = connection.request_json(InternetGetter.TIME_API_URL)
        print(response_d)
        try:
            return response_d["datetime"]
        except KeyError:
            return ""
