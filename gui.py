import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

# Модели данных
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Client:
    def __init__(self, number, fio):
        self.number = number
        self.fio = fio

class Order:
    def __init__(self, number, client, products_qty_dict, date):
        # products_qty_dict: dict {Product: quantity_in_kg}
        self.number = number
        self.client = client
        self.products_qty = products_qty_dict
        self.date = date

# Аналитические функции
def orders_to_df(orders):
    data = []
    for order in orders:
        for product, qty in order.products_qty.items():
            data.append({
                'OrderNumber': order.number,
                'ClientNumber': order.client.number,
                'ClientFIO': order.client.fio,
                'ProductName': product.name,
                'ProductPrice': product.price,
                'Quantity': qty,
                'OrderDate': order.date
            })
    return pd.DataFrame(data)

def top_clients_by_orders(orders, top=5):
    df = orders_to_df(orders)
    if df.empty:
        return pd.DataFrame()
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    result = df.groupby(['ClientNumber', 'ClientFIO'])['OrderNumber'].nunique().sort_values(ascending=False).head(top)
    return result

def order_dynamics(orders, parent_frame):
    df = orders_to_df(orders)
    if df.empty:
        ttk.Label(parent_frame, text="Нет данных для анализа.").pack()
        return
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    df_daily = df.groupby('OrderDate')['OrderNumber'].nunique()
    fig = plt.Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    df_daily.plot(kind='line', marker='o', ax=ax)
    ax.set_title('Динамика заказов по датам')
    ax.set_xlabel('Дата')
    ax.set_ylabel('Количество заказов')
    ax.grid(True)
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    return canvas

def products_chart(orders, parent_frame):
    # Аналитика по товарам
    product_counter = Counter()
    for order in orders:
        for p, qty in order.products_qty.items():
            product_counter[p.name] += qty
    if not product_counter:
        ttk.Label(parent_frame, text="Нет данных по товарам.").pack()
        return
    top_products = product_counter.most_common()
    names = [tp[0] for tp in top_products]
    counts = [tp[1] for tp in top_products]
    fig = plt.Figure(figsize=(6,4))
    ax = fig.add_subplot(111)
    ax.barh(names[::-1], counts[::-1])
    ax.set_title('Популярные товары (по весу кг)')
    ax.set_xlabel('Общее количество в кг')
    ax.set_ylabel('Товары')
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    return canvas

# Основное приложение
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Менеджер интернет-магазина")
        self.geometry("950x850")
        # Изначальный списки
        self.clients = []
        self.orders = []
        self.products_catalog = [
            Product("Сахар", 50),
            Product("Соль", 20),
            Product("Перец черный, молотый", 30),
            Product("Перец красный, молотый", 35),
            Product("Куркума", 50)
        ]
        self.create_widgets()
        self.create_test_orders()

    def create_test_orders(self):
        c1 = Client(1, "Иванов Иван")
        c2 = Client(2, "Петров Петр")
        self.clients.extend([c1, c2])
        # Тестовые заказы с указанием веса
        self.orders.append(Order(101, c1, {self.products_catalog[0]: 2.5, self.products_catalog[1]: 1.0}, datetime(2024,5,1)))
        self.orders.append(Order(102, c1, {self.products_catalog[2]: 0.75}, datetime(2024,5,2)))
        self.orders.append(Order(103, c2, {self.products_catalog[1]: 1.2}, datetime(2024,5,1)))

    def create_widgets(self):
        tabControl = ttk.Notebook(self)
        self.clients_tab = ttk.Frame(tabControl)
        self.orders_tab = ttk.Frame(tabControl)
        self.analysis_tab = ttk.Frame(tabControl)

        tabControl.add(self.clients_tab, text='Клиенты')
        tabControl.add(self.orders_tab, text='Заказы')
        tabControl.add(self.analysis_tab, text='Аналитика')
        tabControl.pack(expand=1, fill="both")

        self.setup_clients_tab()
        self.setup_orders_tab()
        self.setup_analysis_tab()

        def on_tab_changed(event):
            if event.widget.tab(event.widget.index("current"), "text") == 'Аналитика':
                self.load_analysis()

        tabControl.bind("<<NotebookTabChanged>>", on_tab_changed)

    def setup_clients_tab(self):
        frm = ttk.Frame(self.clients_tab)
        frm.pack(padx=10, pady=10, fill='x')

        ttk.Label(frm, text="Номер клиента:").grid(row=0, column=0)
        self.client_number_var = tk.IntVar()
        ttk.Entry(frm, textvariable=self.client_number_var).grid(row=0, column=1)

        ttk.Label(frm, text="ФИО:").grid(row=1, column=0)
        self.client_fio_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.client_fio_var).grid(row=1, column=1)

        ttk.Label(frm, text="Телефон (+79000000000):").grid(row=2, column=0)
        self.client_phone_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.client_phone_var).grid(row=2, column=1)

        ttk.Label(frm, text="Email:").grid(row=3, column=0)
        self.client_email_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.client_email_var).grid(row=3, column=1)

        ttk.Button(frm, text="Добавить клиента", command=self.add_client).grid(row=4, column=0, columnspan=2, pady=10)

        # Кнопки для удаления и редактирования
        btn_frame = ttk.Frame(self.clients_tab)
        btn_frame.pack(padx=10, pady=5, fill='x')
        ttk.Button(btn_frame, text="Удалить выбранного клиента", command=self.delete_selected_client).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать выбранного клиента", command=self.edit_selected_client).pack(side='left', padx=5)

        self.clients_list = tk.Listbox(self.clients_tab)
        self.clients_list.pack(padx=10, pady=10, fill='both', expand=True)
        self.refresh_clients_list()

    def add_client(self):
        try:
            number = self.client_number_var.get()
            fio = self.client_fio_var.get().strip()
            phone = self.client_phone_var.get().strip()
            email = self.client_email_var.get().strip()
            client = Client(number, fio)
            self.clients.append(client)
            self.refresh_clients_list()
            messagebox.showinfo("Успех", "Клиент добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_clients_list(self):
        self.clients_list.delete(0, tk.END)
        for c in self.clients:
            self.clients_list.insert(tk.END, f"{c.number}: {c.fio}")

    def delete_selected_client(self):
        sel = self.clients_list.curselection()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите клиента для удаления")
            return
        index = sel[0]
        try:
            del self.clients[index]
            self.refresh_clients_list()
            messagebox.showinfo("Успех", "Клиент удален")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def edit_selected_client(self):
        sel = self.clients_list.curselection()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите клиента для редактирования")
            return
        index = sel[0]
        client = self.clients[index]
        self.open_edit_client_window(client, index)

    def open_edit_client_window(self, client, index):
        edit_win = tk.Toplevel(self)
        edit_win.title("Редактировать клиента")
        edit_win.geometry("300x200")
        ttk.Label(edit_win, text="Номер клиента:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        number_var = tk.IntVar(value=client.number)
        ttk.Entry(edit_win, textvariable=number_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(edit_win, text="ФИО:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        fio_var = tk.StringVar(value=client.fio)
        ttk.Entry(edit_win, textvariable=fio_var).grid(row=1, column=1, padx=5, pady=5)
        def save():
            try:
                client.number = number_var.get()
                client.fio = fio_var.get()
                self.refresh_clients_list()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        ttk.Button(edit_win, text="Сохранить", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def setup_orders_tab(self):
        frm = ttk.Frame(self.orders_tab)
        frm.pack(padx=10, pady=10, fill='x')

        ttk.Label(frm, text="Номер заказа:").grid(row=0, column=0)
        self.order_number_var = tk.IntVar()
        ttk.Entry(frm, textvariable=self.order_number_var).grid(row=0, column=1)

        ttk.Label(frm, text="Клиент (номер):").grid(row=1, column=0)
        self.order_client_number_var = tk.IntVar()
        ttk.Entry(frm, textvariable=self.order_client_number_var).grid(row=1, column=1)

        ttk.Label(frm, text="Выберите товары и кол-во (в кг):").grid(row=2, column=0, sticky='w')
        self.product_vars = {}
        self.p_qty_vars = {}  # для хранения полей с количеством
        for i, p in enumerate(self.products_catalog):
            var = tk.BooleanVar()
            ttk.Checkbutton(frm, text=f"{p.name} ({p.price} руб.)", variable=var).grid(row=3+i, column=0, sticky='w')
            self.product_vars[p] = var
            # Создаём поле для указывания количества
            qty_var = tk.StringVar(value='1')
            self.p_qty_vars[p] = qty_var
            ttk.Label(frm, text="кг:").grid(row=3+i, column=1, sticky='e')
            ttk.Entry(frm, width=5, textvariable=qty_var).grid(row=3+i, column=2, sticky='w')

        ttk.Button(frm, text="Добавить заказ", command=self.add_order).grid(row=3+i+1, column=0, columnspan=3, pady=10)

        self.orders_list = tk.Listbox(self, height=10)
        self.orders_list.pack(padx=10, pady=10, fill='both', expand=True)
        self.refresh_orders_list()

    def add_order(self):
        try:
            number = self.order_number_var.get()
            client_number = self.order_client_number_var.get()
            client = next((c for c in self.clients if c.number == client_number), None)
            if not client:
                raise ValueError("Клиент с таким номером не найден")
            products_qty = {}
            for p, v in self.product_vars.items():
                if v.get():
                    qty_str = self.p_qty_vars[p].get()
                    try:
                        qty = float(qty_str)
                        if qty <= 0:
                            raise ValueError
                        products_qty[p] = qty
                    except:
                        messagebox.showerror("Ошибка", f"Введите правильное кол-во (в кг) для {p.name}")
                        return
            order = Order(number, client, products_qty, datetime.now())
            self.orders.append(order)
            self.refresh_orders_list()
            messagebox.showinfo("Успех", "Заказ добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_orders_list(self):
        self.orders_list.delete(0, tk.END)
        for o in self.orders:
            total = sum(p.price * qty for p, qty in o.products_qty.items())
            products_str = ", ".join([f"{p.name} ({qty} кг)" for p, qty in o.products_qty.items()])
            self.orders_list.insert(tk.END,
                f"Заказ #{o.number} для {o.client.fio}, Товары: {products_str}, Сумма: {total:.2f} руб.")

    def setup_analysis_tab(self):
        self.analysis_frame = ttk.Frame(self.analysis_tab)
        self.analysis_frame.pack(fill='both', expand=True)

    def load_analysis(self):
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        try:
            order_dynamics(self.orders, self.analysis_frame)
        except Exception as e:
            ttk.Label(self.analysis_frame, text=f"Ошибка графика: {e}").pack()

        try:
            top_clients = top_clients_by_orders(self.orders)
            if top_clients.empty:
                text = "Нет данных по клиентам."
            else:
                text = "Топ клиентов по заказам:\n" + "\n".join(
                    [f"{row['ClientFIO']}: {row['OrderNumber']} заказов" for index, row in top_clients.reset_index().iterrows()]
                )
            ttk.Label(self.analysis_frame, text=text).pack(pady=10)
        except Exception as e:
            ttk.Label(self.analysis_frame, text=f"Ошибка анализа клиентов: {e}").pack()

        # Диаграмма по товарам
        try:
            products_chart(self.orders, self.analysis_frame)
        except Exception as e:
            ttk.Label(self.analysis_frame, text=f"Ошибка по товарам: {e}").pack()

# Запуск
if __name__ == "__main__":
    app = App()
    app.mainloop()