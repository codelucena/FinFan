from datetime import datetime, timedelta
from src.ledger import Ledger
import unittest

class LedgerTest(unittest.TestCase):
  def ledger_buy(self):
    """Buy a stock at given price
    """
    ledger = Ledger("test_ledger", 100000)
    ledger.placeOrder("TEST", "BUY", 100, 100, 100)
    self.assertEqual(len(ledger.stocks_to_holdings.keys()), 1);
  
  def ledger_sell(self):
    """Verify selling a stock
    """
    ledger = Ledger("test_ledger", 100000)
    curr_dt = datetime.strptime("1/02/2022", "%d/%m/%Y")
    ledger.placeOrder("TEST", "BUY", curr_dt, 100, 100)
    curr_dt += timedelta(days=1)
    ledger.placeOrder("TEST", "SELL", curr_dt, 100, 100)
    self.assertEqual(len(ledger.stocks_to_holdings.keys()), 0)
    self.assertEqual(len(ledger.stocks_to_orders.keys()), 1)
    self.assertEqual(len(ledger.stocks_to_orders["TEST"]), 2)

  def ledger_capital_threshold(self):
    """Verify the we consider maximum capital while buying stocks
    """
    ledger = Ledger("test_ledger", 20000)
    curr_dt = datetime.strptime("1/02/2022", "%d/%m/%Y")
    ledger.placeOrder("TEST1", "BUY", curr_dt, 100, 100)
    ledger.placeOrder("TEST2", "BUY", curr_dt, 100, 100)
    self.assertEqual(ledger.min_capital, 0)
    self.assertEqual(len(ledger.stocks_to_holdings.keys()), 2)
    curr_dt += timedelta(days=1)
    self.assertFalse(ledger.placeOrder("TEST3", "BUY", curr_dt, 100, 100))
    self.assertEqual(ledger.min_capital, 0)
    self.assertEqual(len(ledger.stocks_to_holdings.keys()), 2)
    curr_dt += timedelta(days=1)
    ledger.placeOrder("TEST1", "SELL", curr_dt, 100)
    self.assertTrue(ledger.placeOrder("TEST3", "BUY", curr_dt, 100, 100))

if __name__ == '__main__':
    unittest.main()