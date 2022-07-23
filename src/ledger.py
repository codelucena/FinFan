import logging

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
        s += "stock price: " + str(self.price) + "\n"
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
    def __init__(self, name, capital):
        self.name = name
        self.stocks_to_orders = dict()
        self.stocks_to_holdings = dict()
        self.profit_or_loss = 0
        self.capital = capital
        self.init_capital = capital
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
            if self.capital < price * quantity:
                return False
            if stock not in self.stocks_to_holdings:
                logging.info("Buying stock " + stock + " for " + str(price) + "*" + str(quantity) + " at " + str(order_time))
                self.stocks_to_holdings[stock] = buy_order
            else:
                logging.info("Error: stock already present in holdings")
                return False
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
                return False
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
        return True 
