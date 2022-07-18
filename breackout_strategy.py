import logging
import requests

logging.basicConfig(filename='app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

class Order:
    order_time = 0
    order_type = "BUY"
    price = 0
    quantity = 0
    stock = ""
    value = 0
    def __init__(self, stock, order_type, order_time, price, quantity):
        self.price = price
        self.quantity = quantity
        self.order_time = order_time
        self.order_type = order_type
        self.stock = stock
        self.value = quantity * price

class Portifolio:
    stocks_to_holdings = dict()
    def addStock():
        """Adds stock to portifolio """

    def value():
        """Gets value of portifolio"""

    def removeStock():
        """Removes stock from portifolio"""

class Ledger:
    def __init__(self, name):
        self.name = name
        self.stocks_to_orders = dict()
        self.stocks_to_holdings = dict()
        self.profit_or_loss = 0

    def placeOrder(self, stock, order_type, order_time, price, quantity = -1):
        """Places order for 'stock'
        Note: Buy order should be at end of the day
        """
        if order_type == "BUY":
            buy_order = Order(stock, "BUY", order_time, price, quantity)
            if stock not in self.stocks_to_holdings:
                self.stocks_to_holdings[stock] = buy_order
            else:
                logging.info("Error: stock already present in holdings")
                return
            if stock not in self.stocks_to_orders:
                self.stocks_to_orders[stock] = [buy_order]
            else:
                self.stocks_to_orders[stock] += [buy_order]
        elif order_type == "SELL":
            if stock not in self.stocks_to_holdings:
                logging.info("Error: stock not found in holdings")
                return
            # calculate profit or loss
            sell_quantity = quantity
            if quantity == -1:
                sell_quantity = self.stocks_to_holdings[stock].quantity
            curr_value = sell_quantity * price
            print(self.stocks_to_holdings[stock].value)
            self.profit_or_loss += curr_value - self.stocks_to_holdings[stock].value
            # add to list of orders
            sell_order = Order(stock, "SELL", order_time, price, sell_quantity)
            if stock not in self.stocks_to_orders:
                self.stocks_to_orders[stock] = [sell_order]
            else:
                self.stocks_to_orders[stock] += [sell_order]
            # delete from holdings
            del self.stocks_to_holdings[stock]


start_date = "26/11/2021"
# Read Data from Chart Ink
csv = open("strategy_output.csv", 'r')
date_to_stocks = dict()
unique_stocks = dict()
for line in csv.readlines():
    date = line.split(',')[0]
    stock = line.split(',')[1]
    if date in date_to_stocks:
        date_to_stocks[date] += [stock]
    else:
        date_to_stocks[date] = [stock]
    if stock in unique_stocks:
        unique_stocks[stock] += 1
    else:
        unique_stocks[stock] = 1

logging.debug(date_to_stocks)

ledger = Ledger("breakout")
print(unique_stocks)
print(len(unique_stocks))

# Get data from Yahoo Fin
headers = {"X-API-KEY": "4etAFOLMoqsIxANvopXwqJlwILogRz95unVpLsf0", "accept": "application/json"}
request_str = "https://yfapi.net/v8/finance/chart/{stock}.NS?range={range}&region=IN&interval={interval}&lang=en"
# resp = requests.get(request_str.format(stock="SBIN", range="1y", interval="1h"), headers=headers)
# if resp.status_code == 200:
#     logging.info("success")
# else:
#     logging.info("failed to fetch yhf data")
# logging.debug(resp.json())



# for dt in sorted(date_to_stocks.keys()):
#     for hour in dt:
#         for stock in ledger.stocks_to_holdings.key():
#             # should we sell this stock according to our strategy
#             sell_price for hour in 
#             ledger.placeOrder("SELL", stock, )
#     stocks = date_to_stocks[dt]
#     for stock in stocks:
#         # call yhf
#         buy_price = get_buy_price(dt, yhf_data)
#         ledger.placeOrder("BUY", stock, )
