from requests.auth import HTTPBasicAuth
import requests

class Order:
    order_time = 0
    order_type = "BUY"
    price = 0
    quantity = 0
    stock = ""
    value = 0
    def __init__(self, order_time, order_type, price, quantity, stock):
        self.price = price
        self.quantity = quantity
        self.order_time = order_time
        self.order_type = order_type
        self.stock = stock
        self.value = quantity * price

class Portifolio:
    stocks_to_holdings = {}
    def addStock():
        """Adds stock to portifolio """

    def value():
        """Gets value of portifolio"""

    def removeStock():
        """Removes stock from portifolio"""

class Ledger:
    stocks_to_orders = {}
    stocks_to_holdings = {}
    profit_or_loss = 0
    def __init__(self, name):
        self.name = name

    def placeOrder(stock, order_type, order_time, price, quantity = -1):
        """Places order for 'stock'
        Note: Buy order should be at end of the day
        """
        if order_type == "BUY":
            buy_order = Order("BUY", order_time, price, stock, quantity)
            if stock not in stocks_to_holdings:
                stocks_to_holdings[stock] = buy_order
            else:
                print("Error: stock already present in holdings")
                return
            if stock not in stocks_to_orders:
                stocks_to_orders[stock] = [buy_order]
            else:
                stocks_to_orders[stock] += [buy_order]
        elif order_type == "SELL":
            if stock not in stocks_to_holdings:
                print("Error: stock not found in holdings")
                return
            # calculate profit or loss
            sell_quantity = quantity
            if quantity == -1:
                sell_quantity = stocks_to_holdings[stock].quantity
            curr_value = sell_quantity * price
            self.profit_or_loss += curr_val - stocks_to_holdings[stock].value
            # add to list of orders
            sell_order = Order("SELL", order_time, price, sell_quantity, stock)
            if stock not in stocks_to_orders:
                stocks_to_orders[stock] = [sell_order]
            else:
                stocks_to_orders[stock] += [sell_order]
            # delete from holdings
            del stocks_to_holdings[stock]


start_date = "26/11/2021"
# Read Data from Chart Ink
csv = open("strategy_output.csv", 'r')
date_to_stockers = {}
for line in csv.readlines():
    date = line.split(',')[0]
    stock = line.split(',')[1]
    if date in date_to_stockers:
        date_to_stockers[date] += [stock]
    else:
        date_to_stockers[date] = [stock]

print(date_to_stockers)

ledger = Ledger("breakout")

# Get data from Yahoo Fin
headers = {"X-API-KEY": "4etAFOLMoqsIxANvopXwqJlwILogRz95unVpLsf0", "accept": "application/json"}
request_str = "https://yfapi.net/v8/finance/chart/{stock}.NS?range={range}&region=IN&interval={interval}&lang=en"
resp = requests.get(request_str.format(stock="HDFCBANK", range="1y", interval="1h"), headers=headers)
if resp.status_code == 200:
    print("success")
else:
    print("failed to fetch yhf data")
print(resp.json())

# for dt in sorted(date_to_stockers.keys()):
#     for hour in dt:
#         for stock in ledger.stocks_to_holdings.key():
#             # should we sell this stock according to our strategy
#             sell_price for hour in 
#             ledger.placeOrder("SELL", stock, )
#     stocks = date_to_stockers[dt]
#     for stock in stocks:
#         # call yhf
#         buy_price = get_buy_price(dt, yhf_data)
#         ledger.placeOrder("BUY", stock, )
