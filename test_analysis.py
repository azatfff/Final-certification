import unittest
from db import Database
from analysis import top_clients_by_orders

class TestAnalysis(unittest.TestCase):
    def test_plot_top_clients_runs(self):
        db = Database(":memory:")
        try:
            top_clients_by_orders(db.get_orders())
        except Exception as e:
            self.fail(f"top_clients_by_orders вызвал исключение: {e}")

if __name__ == '__main__':
    unittest.main()