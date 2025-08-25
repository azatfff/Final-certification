"""
Модуль работы с данными — сохранение/загрузка из JSON и CSV (без SQL),
функции добавления и поиска.
"""

import sqlite3
from models import Client, Product, Order
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                number TEXT PRIMARY KEY,
                fio TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                number TEXT PRIMARY KEY,
                client_number TEXT,
                date TEXT,
                FOREIGN KEY(client_number) REFERENCES clients(number)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_products (
                order_number TEXT,
                product_name TEXT,
                product_price REAL,
                FOREIGN KEY(order_number) REFERENCES orders(number)
            )
        ''')
        self.conn.commit()

    def insert_client(self, client):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO clients (number, fio, phone, email)
            VALUES (?, ?, ?, ?)
        ''', (client.number, client.fio, client.phone, client.email))
        self.conn.commit()

    def insert_order(self, order):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO orders (number, client_number, date)
            VALUES (?, ?, ?)
        ''', (order.number, order.client.number, order.date.isoformat()))
        for product in order.products:
            cursor.execute('''
                INSERT INTO order_products (order_number, product_name, product_price)
                VALUES (?, ?, ?)
            ''', (order.number, product.name, product.price))
        self.conn.commit()

    def get_clients(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT number, fio, phone, email FROM clients')
        rows = cursor.fetchall()
        return [Client(*row) for row in rows]

    def get_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT number, client_number, date FROM orders')
        orders_data = cursor.fetchall()

        clients = {c.number: c for c in self.get_clients()}
        orders = []
        for number, client_number, date_str in orders_data:
            cursor.execute('''
                SELECT product_name, product_price FROM order_products WHERE order_number=?
            ''', (number,))
            products_data = cursor.fetchall()
            products = [Product(name, price) for name, price in products_data]
            date = datetime.fromisoformat(date_str)
            client = clients.get(client_number)
            order = Order(number, client, products, date)
            orders.append(order)
        return orders

    def close(self):
        self.conn.close()