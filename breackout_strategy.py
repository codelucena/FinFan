from datetime import datetime
from os.path import exists
import logging
import requests
import json

logging.basicConfig(filename='app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

class StockPosition:
    def __init__(self, stock, openv, closev, volume):
        self.stock = stock
        self.openv = openv
        self.closev = closev
        self.volume = volume

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


start_date = datetime.strptime("01/05/2022", "%d/%m/%Y")
end_date = datetime.strptime("01/07/2022", "%d/%m/%Y")
# Read Data from Chart Ink
csv = open("strategy_output.csv", 'r')
date_to_stocks = dict()
unique_stocks = dict()
for line in csv.readlines():
    date = line.split(',')[0]
    stock = line.split(',')[1]
    curr_dt = datetime.strptime(date, "%d-%m-%Y")
    if curr_dt > end_date or curr_dt < start_date:
        continue
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

unique_stocks_file = open("unique_stocks.txt", 'w')
for stock in unique_stocks.keys():
    unique_stocks_file.write(stock + "\n")

# construct stock history
stock_history = {}
for stock in unique_stocks:
    stock_history[stock] = {}
    if not exists(stock + ".json"):
        print("Stock doesn't exist, please fetch : " + stock)
        continue
    stock_file = open("charts/" + stock + ".json", 'r')
    print("reading " + stock)
    data = json.load(stock_file)
    timestamp_list = data["chart"]["result"][0]["timestamp"]
    volume_list = data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
    close_list = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    open_list = data["chart"]["result"][0]["indicators"]["quote"][0]["open"]  
    num_entries = len(data["chart"]["result"][0]["timestamp"])
    num_indicators = len(data["chart"]["result"][0]["indicators"]["quote"][0]["volume"])
    assert(num_entries == num_indicators)
    for i in range(num_entries):
        stock_pos = StockPosition(stock, open_list[i], close_list[i], volume_list[i])
        stock_history[stock][timestamps[i]] = stock_pos
    

for dt in sorted(date_to_stocks.keys()):
    for stock in ledger.stocks_to_holdings.key():
        # should we sell this stock according to our strategy
        sell_price for hour in 
        ledger.placeOrder("SELL", stock, )
    stocks = date_to_stocks[dt]
    for stock in stocks:
        # call yhf
        buy_price = get_buy_price(dt, yhf_data)
        ledger.placeOrder("BUY", stock, )
