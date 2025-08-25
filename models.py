import re
from datetime import datetime

class Client:
    """Класс клиента с ФИО, телефоном, email и валидацией."""

    phone_pattern = re.compile(r'^\+7\d{10}$')
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

    def __init__(self, number, fio, phone, email):
        self.number = number
        self.fio = fio
        self.phone = phone
        self.email = email
        self.validate()

    def validate(self):
        """Проверка телефона и email, выбрасывает исключение при ошибке."""
        if not Client.phone_pattern.match(self.phone):
            raise ValueError(
                f"Неверный формат телефона: {self.phone}. Телефон должен начинаться с +7 и содержать 10 цифр после.")
        if not Client.email_pattern.match(self.email):
            raise ValueError(f"Неверный формат email: {self.email}")

    def __repr__(self):
        return f"Client({self.number}, {self.fio})"

class Product:
    """Класс товара с названием и ценой."""

    def __init__(self, name, price):
        self.name = name
        self.price = float(price)

    def __repr__(self):
        return f"Product({self.name}, {self.price})"

class Order:
    """Класс заказа: номер, клиент, список товаров, дата и расчет стоимости."""

    def __init__(self, number, client, products, date=None):
        self.number = number
        self.client = client
        self.products = products
        self.date = date or datetime.now()

    @property
    def total_cost(self):
        """Суммарная стоимость товаров в заказе."""
        return sum(p.price for p in self.products)

    def __repr__(self):
        return f"Order({self.number}, Client={self.client.number}, Total={self.total_cost:.2f})"