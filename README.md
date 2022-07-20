# FinFan

python3 breakout_strategy.py < input.txt

if charts are missing for some stocks
run python3 fetch_chart.py after running the above command and rerun breakout_strategy.py

input file will have three lines
- upper threshold % (minimum profit for exit) (default = 10)
- lower threshold % (maximum loss for exit) (default = 2)
- budget for each stock (defaut = 1000000)

logs are present in logs/
holdings and orders files are present in output/

