import unittest
from breackout_strategy import Ledger

class LedgerTest(unittest.TestCase):
  def ledger_buy(self):
    """Buy a stock at given price
    """
    print("running test 1")
    ledger = Ledger("tests_ledger")
    ledger.placeOrder("TEST", "BUY", 100, 100, 100)
    self.assertEqual(len(ledger.stocks_to_holdings.keys()), 1);
  
  def ledger_sell(self):
    """Verify selling a stock
    """
    print("running test 1")
    ledger = Ledger("tests_ledger")
    ledger.placeOrder("TEST", "BUY", 100, 100, 100)
    ledger.placeOrder("TEST", "SELL", 100, 100, 100)
    self.assertEqual(len(ledger.stocks_to_holdings.keys()), 0)
    self.assertEqual(len(ledger.stocks_to_orders.keys()), 1)
    self.assertEqual(len(ledger.stocks_to_orders["TEST"]), 2)
    

if __name__ == '__main__':
    unittest.main()