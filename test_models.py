import unittest
from models import Client, Product, Order

class TestModels(unittest.TestCase):
    def test_email_validation(self):
        with self.assertRaises(ValueError):
            Client(1, "Name", "bademail", "+7 900 000 00 00")

    def test_phone_validation(self):
        with self.assertRaises(ValueError):
            Client(1, "Name", "test@example.com", "12345")

    def test_order_total_cost(self):
        p1 = Product("Test1", 100)
        p2 = Product("Test2", 300)
        order = Order(1, 1, [p1, p2])
        self.assertEqual(order.total_cost, 400)

if __name__ == '__main__':
    unittest.main()
