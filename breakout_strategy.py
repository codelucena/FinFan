from datetime import datetime
from datetime import timedelta
from os.path import exists
import copy
import logging
import os
import requests
import json

logging.basicConfig(filename='logs/app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

class StockPosition:
    def __init__(self, stock, openv, closev, volume, timestamp):
        self.stock = stock
        self.openv = openv
        self.closev = closev
        self.volume = volume
        self.time = timestamp

class Order:
    order_time = None
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

    def ToString(self):
        s = ""
        s += "stock : " + self.stock + "\n"
        s += "order_type: " + self.order_type + "\n"
        s += "order_value: " + str(self.value) + "\n"
        s += "order_time: " + str(self.order_time) + "\n"
        return s
    
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
        self.capital = 100000000
        self.init_capital = 100000000
        self.min_capital = 100000000

    def printOrders(self, filename):
        f = open(filename, 'w')
        r = ""
        for stock in self.stocks_to_orders.keys():
            r += "=" * 100 + "\n"
            r += stock + ":\n"
            for order in self.stocks_to_orders[stock]:
                r += "*" * 50 + "\n"
                r += order.ToString()
        f.write(r)
        f.close()

    def printHoldings(self, filename):
        f = open(filename, 'w')
        r = ""
        for stock in self.stocks_to_holdings.keys():
            r += "*" * 100 + "\n"
            r += self.stocks_to_holdings[stock].ToString()
        f.write(r)
        f.close()

    def placeOrder(self, stock, order_type, order_time, price, quantity = -1):
        """Places order for 'stock'
        Note: Buy order should be at end of the day
        """
        if order_type == "BUY":
            buy_order = Order(stock, "BUY", order_time, price, quantity)
            if stock not in self.stocks_to_holdings:
                logging.info("Buying stock " + stock + " for " + str(price) + "*" + str(quantity) + " at " + str(order_time))
                self.stocks_to_holdings[stock] = buy_order
            else:
                logging.info("Error: stock already present in holdings")
                return
            if stock not in self.stocks_to_orders:
                self.stocks_to_orders[stock] = [buy_order]
            else:
                self.stocks_to_orders[stock] += [buy_order]
            self.capital -= price * quantity
            self.min_capital = min(self.min_capital, self.capital)
        elif order_type == "SELL":
            logging.info("Received sell order")
            if stock not in self.stocks_to_holdings:
                logging.info("Error: stock not found in holdings")
                return
            # calculate profit or loss
            sell_quantity = quantity
            if quantity == -1:
                sell_quantity = self.stocks_to_holdings[stock].quantity
            curr_value = sell_quantity * price
            self.profit_or_loss += curr_value - self.stocks_to_holdings[stock].value
            self.capital +=  curr_value
            if curr_value - self.stocks_to_holdings[stock].value > 0:
                logging.debug("Exit for a profit of " \
                    + str(curr_value - self.stocks_to_holdings[stock].value) \
                    + " curr_value: " + str(curr_value) \
                    + " old: " + str(self.stocks_to_holdings[stock].value))
            else:
                logging.debug("Exit for a loss of " \
                    + str(curr_value - self.stocks_to_holdings[stock].value) \
                    + " curr_value: " + str(curr_value) \
                    + " old: " + str(self.stocks_to_holdings[stock].value))
            # add to list of orders
            sell_order = Order(stock, "SELL", order_time, price, sell_quantity)
            if stock not in self.stocks_to_orders:
                logging.info("Selling " + sell_quantity + " stocks of " + stock + " at " + str(price))
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
    if curr_dt in date_to_stocks:
        date_to_stocks[curr_dt] += [stock]
    else:
        date_to_stocks[curr_dt] = [stock]
    if stock in unique_stocks:
        unique_stocks[stock] += 1
    else:
        unique_stocks[stock] = 1
logging.debug("Date to Stocks")
logging.debug(date_to_stocks)

ledger = Ledger("breakout")

unique_stocks_file = open("unique_stocks.txt", 'w')
for stock in unique_stocks.keys():
    unique_stocks_file.write(stock + "\n")

# construct stock history
stock_history = {}
for stock in unique_stocks:
    stock_history[stock] = {}
    stock_filename = "charts/" + stock + ".json"
    if not exists(stock_filename):
        print("Stock doesn't exist, please fetch : " + stock)
        continue
    stock_file = open(stock_filename, 'r')
    logging.info("reading " + stock)
    data = json.load(stock_file)
    timestamp_list = data["chart"]["result"][0]["timestamp"]
    volume_list = data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
    close_list = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    open_list = data["chart"]["result"][0]["indicators"]["quote"][0]["open"]  
    num_entries = len(data["chart"]["result"][0]["timestamp"])
    num_indicators = len(data["chart"]["result"][0]["indicators"]["quote"][0]["volume"])
    assert(num_entries == num_indicators)
    for i in range(num_entries):
        ts = datetime.fromtimestamp(timestamp_list[i])
        stock_pos = StockPosition(stock, open_list[i], close_list[i], volume_list[i], ts)
        stock_history[stock][timestamp_list[i]] = stock_pos
    
up_end = int(input())
lo_end = int(input())
budget_per_stock = int(input())

for dt in sorted(date_to_stocks.keys()):
    start_dt = dt
    end_dt = start_dt + timedelta(days=1)
    logging.debug("processing date : " + str(dt) + " and # holdings : " + str(len(ledger.stocks_to_holdings.keys())))
    curr_holdings = copy.deepcopy(ledger.stocks_to_holdings)
    for stock in curr_holdings.keys():
        order = curr_holdings[stock]
        # should we sell this stock according to our strategy
        assert(order.order_type == "BUY")
        curr_stock = stock_history[stock]
        logging.debug("Processing stock " + stock + " with # ts : " + str(len(curr_stock.keys())))
        for ts in sorted(curr_stock.keys()):
            curr_time = datetime.fromtimestamp(ts)
            logging.debug(curr_time)
            if curr_time < start_dt:
                continue
            elif curr_time >= end_dt:
                break
            curr_pos = curr_stock[ts]
            def validate(pos):
                if pos.closev is None:
                    logging.debug("closev is none : " + pos.stock)
                    return False
                if pos.volume is None:
                    logging.debug("volume is none : " + pos.stock)
                    return False
                return True
            if not validate(curr_pos):
                logging.info("Validation failed for " + stock)
                continue;
            exit_condition = curr_pos.closev > \
                 (1 + up_end * 0.01) * order.price or curr_pos.closev < \
                 (1 - lo_end * 0.01) * order.price
            last_pos = curr_pos
            if exit_condition:
                logging.info("Exit condition met for " + stock + " curr-price : " + str(curr_pos.closev) + " buy-price : " + str(order.price))
                ledger.placeOrder(stock, "SELL", curr_time, curr_pos.closev)
                break
            else:
                logging.info("Exit condition failed for " + stock + " curr-price : " + str(curr_pos.closev) + " buy-price : " + str(order.price)) 
    stocks = date_to_stocks[dt]
    print(stocks)
    for stock in stocks:
        # call yhf
        curr_stock = stock_history[stock]
        pos = None
        curr_time = None
        for ts in sorted(curr_stock.keys()):
            curr_time = datetime.fromtimestamp(ts)
            if curr_time < start_dt:
                continue
            elif curr_time >= end_dt:
                break
            pos = curr_stock[ts]
        if pos is not None and pos.closev is not None:
            quantity = budget_per_stock/pos.closev
            ledger.placeOrder(stock, "BUY", pos.time, pos.closev, quantity)
            logging.debug("Buy : " + stock)
        else:
            logging.error("Couldn't get price")

print("capital utilized : " + str(int(ledger.init_capital - ledger.min_capital)))
print("profit/loss: " + str(int(ledger.profit_or_loss)))
os.makedirs("output")
ledger.printOrders("output/orders.txt")
ledger.printHoldings("output/holdings.txt")
