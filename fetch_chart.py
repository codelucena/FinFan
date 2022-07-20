from os.path import exists
import logging
import requests
import json

logging.basicConfig(filename='fetcher.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

f = open("unique_stocks.txt", 'r')
for line in f.readlines():
  stock = line.strip()
  chart_name = "charts/" + stock + ".json"
  if exists(chart_name):
    print("File already exists " + chart_name)
  else:
    print("fetching " + chart_name)
    headers = {"X-API-KEY": "4etAFOLMoqsIxANvopXwqJlwILogRz95unVpLsf0", "accept": "application/json"}
    request_str = "https://yfapi.net/v8/finance/chart/{stock}.NS?range={range}&region=IN&interval={interval}&lang=en"
    resp = requests.get(request_str.format(stock=stock, range="1y", interval="1h"), headers=headers)
    if resp.status_code == 200:
        logging.info("success")
    else:
        logging.info("failed to fetch yhf data")
    logging.debug(resp.json())
    s = open(chart_name, 'w')
    json.dump(resp.json(), s)
