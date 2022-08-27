from datetime import datetime
from datetime import timedelta
from math import floor
from os.path import exists
from ledger import Ledger, StockPosition
import matplotlib.pyplot as plt
import numpy as np
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
        high_list = data["chart"]["result"][0]["indicators"]\
                        ["quote"][0]["high"]
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
                                      high_list[i],
                                      ts)
            stock_history[stock][ts] = stock_pos
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

def getStocksNDayMax(num_days, stocks, stock_history, date):
    """Returns map with 90 days max for the stocks given
    """
    stock_n_day_max = {}
    for stock in stocks:
        stock_n_day_max[stock] = 0
        keys = stock_history[stock].keys()
        curr_time = date - timedelta(days=num_days) + timedelta(hours=9) + timedelta(minutes=15)
        while curr_time < date - timedelta(days=1):
            if curr_time in stock_history[stock]:
                if stock_history[stock][curr_time].high is None:
                    logging.error("high is none for : " + stock + " at " + str(curr_time))
                else:
                    stock_n_day_max[stock] = max(stock_n_day_max[stock], \
                                                stock_history[stock][curr_time].high)
            curr_time += timedelta(hours=1)
    return stock_n_day_max


def generateGraph(times, prices, entry_points, exit_points, stock):
    """Generates a graph with entry and exit points marked
    """
    f = plt.figure()
    xpoints = np.array(times)
    ypoints = np.array(prices)
    plt.plot(xpoints, ypoints, linewidth=1, color="green", alpha=0.2)
    for entry in entry_points:
        plt.scatter(entry[0], entry[1], marker="^", color="blue", s=12)
    for exit in exit_points:
        plt.scatter(exit[0], exit[1], marker="X", color="red", s=12)
    plt.savefig("graphs/{}.pdf".format(stock))
    plt.close(f)

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
    stocks_traded = {}
    while dt <= end_date:
        logging.debug("processing date : " + str(dt) + " and # holdings : " + \
                      str(len(ledger.stocks_to_holdings.keys())))
        stocks_120d_max = dict()
        stocks_suggested = []
        for i in range(3):
            curr_dt = dt - timedelta(days=(i + 1))
            if curr_dt in date_to_stocks:
                curr_stocks = date_to_stocks[curr_dt]
                for stock in date_to_stocks[curr_dt]:
                    stocks_suggested += [[i+1, stock]]
                stocks_120d_max.update(getStocksNDayMax(120, curr_stocks, stock_history, dt - timedelta(days=i+1)))
        curr_time = dt + timedelta(hours=9) + timedelta(minutes=15)
        end_time = dt + timedelta(hours=15) + timedelta(minutes=15)
        bought_today = []
        while curr_time <= end_time:
            for _stock in stocks_suggested:
                stock = _stock[1]
                retest_d = _stock[0]
                if stock not in stocks_traded:
                    stocks_traded[stock] = dict()
                    stocks_traded[stock]["entries"] = []
                    stocks_traded[stock]["exits"] = []
                if curr_time != end_time and False:
                    break
                logging.info("BUY: processing " + stock + " at " + str(curr_time))
                if curr_time not in stock_history[stock]:
                    logging.debug(str(curr_time) + " not in " + stock)
                    continue
                curr_pos = stock_history[stock][curr_time]
                if stock in bought_today:
                    logging.debug("Already bought " + stock)
                    continue
                if curr_pos.closev is None:
                    logging.info("closev is none for : " + stock + " at "\
                                 + str(curr_time))
                elif curr_pos.closev <= stocks_120d_max[stock] * 1.01 and \
                        curr_pos.closev >= (stocks_120d_max[stock] - 0.5) and \
                        curr_pos.closev > 10:
                    if curr_pos.closev != curr_pos.openv:
                        quantity = floor(budget_per_stock/curr_pos.closev)
                        logging.info("Buy stock : " + stock)
                        if ledger.placeOrder(stock, "BUY", curr_pos.time,
                                        curr_pos.closev, quantity) == True:
                            bought_today += [stock]
                            stocks_traded[stock]["entries"].append([curr_time, curr_pos.closev])
                            logging.info("Successfully bought " + stock + " for " + str(retest_d) + " retest")
                        else:
                            logging.info("Couldn't buy stock : " + stock)
                    else:
                        logging.info("Close is same as open " + str(curr_pos.closev)\
                                      + " for " + stock)
                else:
                    logging.info("90dmax not reached for " + stock + " at " \
                                 + str(curr_time) + " 90dm: " \
                                 + str(stocks_120d_max[stock]) \
                                 + " val: " + str(curr_pos.closev))
            curr_holdings = copy.deepcopy(ledger.stocks_to_holdings)
            for stock in curr_holdings.keys():
                order = curr_holdings[stock]
                logging.info("SELL: processing " + stock + " at " + str(curr_time))
                if curr_time not in stock_history[stock]:
                    logging.info(stock + " not found at " + str(curr_time))
                    continue
                curr_pos = stock_history[stock][curr_time]
                if curr_pos.closev is None:
                    logging.info("closev is none for : " + stock + " at "\
                                  + str(curr_time))
                    continue
                exit_condition = \
                    curr_pos.closev > (1 + up_end * 0.01) * order.price or \
                    curr_pos.closev < (1 - lo_end * 0.01) * order.price
                if dt == start_date:
                    exit_condition |= \
                        curr_pos.openv > (1 + up_end * 0.01) * order.price or \
                        curr_pos.openv < (1 - lo_end * 0.01) * order.price
                last_pos = curr_pos
                if exit_condition:
                    logging.info("Exit condition met for " + stock + \
                                    " curr-price : " + str(curr_pos.closev) + \
                                    " buy-price : " + str(order.price))
                    if ledger.placeOrder(stock, "SELL", curr_time, curr_pos.closev):
                        logging.info("Succefully sold " + stock)
                    stocks_traded[stock]["exits"].append([curr_time, curr_pos.closev])
                else:
                    logging.info("Exit condition failed for " + stock + \
                                    " curr-price : " + str(curr_pos.closev) + \
                                    " buy-price : " + str(order.price))
            curr_time += timedelta(hours=1)
        for stock in stocks_suggested:
            if stock[1] not in ledger.stocks_to_holdings:
                logging.info("Stock not bought " + stock[1] + " at " + str(dt)\
                              + " 120dm " + str(stocks_120d_max[stock[1]]))
        ledger.cap_util_statement.append([str(dt), ledger.capital])
        dt += timedelta(days=1)
    # Generate graphs for all stocks
    for stock in stocks_traded.keys():
        curr_time = start_date + timedelta(minutes=15)
        times = []
        prices = []
        while curr_time <= end_date:
            curr_time += timedelta(hours=1)
            if curr_time not in stock_history[stock]:
                continue
            times.append(curr_time)
            prices.append(stock_history[stock][curr_time].closev)
        if len(stocks_traded[stock]["entries"]) > 0:
            generateGraph(times, prices, stocks_traded[stock]["entries"], stocks_traded[stock]["exits"], stock)
    print("capital utilized : " + \
          str(int(ledger.init_capital - ledger.min_capital)))
    print("profit/loss: " + str(int(ledger.profit_or_loss)))
    print("profit/lost %: " + str((int(ledger.profit_or_loss) * 100)/\
                              int(ledger.init_capital - ledger.min_capital)))
    print("num_sells: " + str(ledger.num_sells) + " num_losses: "\
          + str(ledger.num_losses))
    print("num_buys: " + str(ledger.num_buys))
    print("loss % : " + str((ledger.num_losses * 100)/ledger.num_sells))
    if not exists("output"):
        os.makedirs("output")
    ledger.printOrders("output/orders_{}.txt".format(strategy_name))
    ledger.printHoldings("output/holdings_{}.txt".format(strategy_name))
    ledger.printPlStatement("output/pl_statement_{}.csv".format(strategy_name))
    ledger.printCaptialUtilizedStatement("output/cap_remaining_daily_{}.csv".format(strategy_name))

if __name__ == "__main__":
    run()
