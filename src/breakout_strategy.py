from datetime import datetime
from datetime import timedelta
from math import floor
from os.path import exists
from ledger import Ledger, StockPosition
import copy
import logging
import os
import requests
import json


logging.basicConfig(filename='logs/app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


def readStrategyOutput(csv_name, start_date, end_date):
    # Read Data from Chart Ink
    csv = open(csv_name, 'r')
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
    unique_stocks_file = open("data/unique_stocks.txt", 'w')
    for stock in unique_stocks.keys():
        unique_stocks_file.write(stock + "\n")
    logging.debug("number of unique_stocks : " + str(len(unique_stocks.keys())))
    return date_to_stocks, unique_stocks

def getStockHistory(unique_stocks):
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
        volume_list = data["chart"]["result"][0]["indicators"]\
                          ["quote"][0]["volume"]
        close_list = data["chart"]["result"][0]["indicators"]\
                         ["quote"][0]["close"]
        open_list = data["chart"]["result"][0]["indicators"]\
                        ["quote"][0]["open"]  
        num_entries = len(data["chart"]["result"][0]["timestamp"])
        num_indicators = len(data["chart"]["result"][0]["indicators"]\
                                 ["quote"][0]["volume"])
        assert(num_entries == num_indicators)
        for i in range(num_entries):
            ts = datetime.fromtimestamp(timestamp_list[i])
            stock_pos = StockPosition(stock,
                                      open_list[i],
                                      close_list[i],
                                      volume_list[i],
                                      ts)
            stock_history[stock][timestamp_list[i]] = stock_pos
    return stock_history

def readInput():
    """Reads input from input.txt
    up_end : Maximum positive % of change before exiting the stock
    lo_end : Maximum negative % of change before exiting the stock
    budget_per_stock : Maximum budget per stock that can be used.
    maximum_overall_budget : Maximum budget available for all the stocks
                             combined
    start_date : start date (%d/%m/%Y)
    end_date : end date (%d/%m/%Y)
    """
    up_end = int(input())
    lo_end = int(input())
    budget_per_stock = int(input())
    maximum_overall_budget = int(input())
    start_date = str(input())
    end_date = str(input())
    csv_name = str(input())
    return up_end, lo_end, budget_per_stock, maximum_overall_budget,\
           start_date, end_date, csv_name

def run():
    # read input
    up_end, lo_end, budget_per_stock, maximum_overall_budget,\
        start_date, end_date, csv_name = readInput()
    # create ledger
    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")
    strategy_name = csv_name.split(".")[0].split("/")[2]
    ledger = Ledger("strategy_name", maximum_overall_budget)
    date_to_stocks, unique_stocks = readStrategyOutput(csv_name, start_date, end_date)
    stock_history = getStockHistory(unique_stocks)
    dt = start_date
    while dt <= end_date:
        start_dt = dt
        end_dt = start_dt + timedelta(days=1)
        logging.debug("processing date : " + str(dt) + " and # holdings : " + \
                      str(len(ledger.stocks_to_holdings.keys())))
        curr_holdings = copy.deepcopy(ledger.stocks_to_holdings)
        for stock in curr_holdings.keys():
            order = curr_holdings[stock]
            # should we sell this stock according to our strategy
            assert(order.order_type == "BUY")
            curr_stock = stock_history[stock]
            logging.debug("Processing stock " + stock + " with # ts : " + \
                          str(len(curr_stock.keys())))
            keys = list(curr_stock.keys())
            for ts in sorted(keys[int(len(keys)/2):]):
                curr_time = datetime.fromtimestamp(ts)
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
                    logging.info("Exit condition met for " + stock + \
                                 " curr-price : " + str(curr_pos.closev) + \
                                 " buy-price : " + str(order.price))
                    ledger.placeOrder(stock, "SELL", curr_time, curr_pos.closev)
                    break
                else:
                    logging.info("Exit condition failed for " + stock + \
                                 " curr-price : " + str(curr_pos.closev) + \
                                 " buy-price : " + str(order.price))
        if dt not in date_to_stocks:
            dt += timedelta(days=1)
            continue
        stocks = date_to_stocks[dt]
        logging.info("stocks: " + str(stocks))
        for stock in stocks:
            # call yhf
            curr_stock = stock_history[stock]
            pos = None
            curr_time = None
            daily_volume = 0
            for ts in sorted(curr_stock.keys()):
                curr_time = datetime.fromtimestamp(ts)
                if curr_time < start_dt:
                    continue
                elif curr_time >= end_dt:
                    break
                if curr_stock[ts].volume != None:
                    daily_volume += curr_stock[ts].volume
                    logging.info("Volume is not none")
                else:
                    logging.info("Volume is none")
                pos = curr_stock[ts]
            logging.info("volume for stock: " + stock + " at: " + str(ts) + " is " + str(daily_volume))
            if pos is not None and pos.closev is not None:
                quantity = floor(budget_per_stock/pos.closev)
                ledger.placeOrder(stock, "BUY", pos.time, pos.closev, quantity)
                logging.debug("Buy : " + stock)
            else:
                logging.error("Couldn't get price")
        dt += timedelta(days=1)
    print("capital utilized : " + \
          str(int(ledger.init_capital - ledger.min_capital)))
    print("profit/loss: " + str(int(ledger.profit_or_loss)))
    print("profit/lost %: " + str((int(ledger.profit_or_loss) * 100)/int(ledger.init_capital - ledger.min_capital)))
    print("num_sells: " + str(ledger.num_sells) + " num_losses: " + str(ledger.num_losses))
    print("loss % : " + str((ledger.num_losses * 100)/ledger.num_sells))
    if not exists("output"):
        os.makedirs("output")
    ledger.printOrders("output/orders_{}.txt".format(strategy_name))
    ledger.printHoldings("output/holdings_{}.txt".format(strategy_name))
    ledger.printPlStatement("output/pl_statement_{}.txt".format(strategy_name))

if __name__ == "__main__":
    run()
