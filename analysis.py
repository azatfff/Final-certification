"""
Функции анализа и визуализации с использованием pandas, matplotlib, seaborn.
"""

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Client:
    def __init__(self, number, fio):
        self.number = number
        self.fio = fio

class Order:
    def __init__(self, number, client, products, date):
        self.number = number
        self.client = client
        self.products = products
        self.date = date

def orders_to_df(orders):
    data = []
    for order in orders:
        for product in order.products:
            data.append({
                'OrderNumber': order.number,
                'ClientNumber': order.client.number,
                'ClientFIO': order.client.fio,
                'ProductName': product.name,
                'ProductPrice': product.price,
                'OrderDate': order.date
            })
    return pd.DataFrame(data)

def top_clients_by_orders(orders, top=5):
    df = orders_to_df(orders)
    top_clients = df.groupby(['ClientNumber', 'ClientFIO'])['OrderNumber'].nunique().sort_values(ascending=False).head(top)
    print("Топ клиентов по количеству заказов:")
    print(top_clients)
    return top_clients

def order_dynamics(orders):
    df = orders_to_df(orders)
    df_daily = df.groupby('OrderDate')['OrderNumber'].nunique()
    df_daily.plot(kind='line', marker='o')
    plt.title('Динамика заказов по датам')
    plt.xlabel('Дата')
    plt.ylabel('Количество заказов')
    plt.grid(True)
    plt.show()
    return df_daily

# Создаем тестовые данные
client1 = Client(1, "Иванов Иван")
client2 = Client(2, "Петров Петр")

product1 = Product("Товар1", 100)
product2 = Product("Товар2", 200)

orders = [
    Order(101, client1, [product1, product2], datetime(2024, 5, 1)),
    Order(102, client1, [product1], datetime(2024, 5, 2)),
    Order(103, client2, [product2], datetime(2024, 5, 1)),
]

# Вызов функций
df = orders_to_df(orders)
print(df)

top_clients_by_orders(orders)
order_dynamics(orders)