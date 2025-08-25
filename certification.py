import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

clients = []
orders = []

# Функции работы с клиентами
def add_client(name, email, phone):
    clients.append({"id": len(clients) + 1, "name": name, "email": email, "phone": phone})
    refresh_clients()

def refresh_clients():
    for row in tree_clients.get_children():
        tree_clients.delete(row)
    for c in clients:
        tree_clients.insert("", "end", values=(c["id"], c["name"], c["email"], c["phone"]))

# Функции работы с заказами
def add_order(client_id, products_str):
    products = []
    for p in products_str.split(";"):
        if p.strip():
            name, qty, price = p.strip().split(",")
            products.append({"name": name.strip(), "qty": int(qty), "price": float(price)})
    orders.append({
        "id": len(orders) + 1,
        "client_id": int(client_id),
        "products": products
    })
    refresh_orders()

def refresh_orders(filter_client=None, sort_by=None):
    for row in tree_orders.get_children():
        tree_orders.delete(row)
    filtered = orders
    if filter_client:
        filtered = [o for o in orders if str(o["client_id"]) == str(filter_client)]
    if sort_by == "id":
        filtered.sort(key=lambda x: x["id"])
    elif sort_by == "client_id":
        filtered.sort(key=lambda x: x["client_id"])
    for o in filtered:
        products_str = ", ".join([f'{p["name"]}×{p["qty"]}' for p in o["products"]])
        tree_orders.insert("", "end", values=(o["id"], o["client_id"], products_str))

# Импорт/Экспорт данных
def export_data():
    file = filedialog.asksaveasfilename(defaultextension=".json",
                                        filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")])
    if not file:
        return
    if file.endswith(".json"):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({"clients": clients, "orders": orders}, f, ensure_ascii=False, indent=4)
    elif file.endswith(".csv"):
        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Clients"])
            writer.writerow(["id", "name", "email", "phone"])
            for c in clients:
                writer.writerow([c["id"], c["name"], c["email"], c["phone"]])
            writer.writerow([])
            writer.writerow(["Orders"])
            writer.writerow(["id", "client_id", "products"])
            for o in orders:
                products_str = "; ".join([f'{p["name"]},{p["qty"]},{p["price"]}' for p in o["products"]])
                writer.writerow([o["id"], o["client_id"], products_str])
    messagebox.showinfo("Экспорт", "Данные успешно экспортированы")

def import_data():
    file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")])
    if not file:
        return
    global clients, orders
    if file.endswith(".json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            clients = data.get("clients", [])
            orders = data.get("orders", [])
    elif file.endswith(".csv"):
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            clients = []
            orders = []
            mode = None
            for row in rows:
                if not row:
                    continue
                if row[0] == "Clients":
                    mode = "clients"
                    continue
                elif row[0] == "Orders":
                    mode = "orders"
                    continue
                if mode == "clients" and row[0].isdigit():
                    clients.append({
                        "id": int(row[0]),
                        "name": row[1],
                        "email": row[2],
                        "phone": row[3]
                    })
                elif mode == "orders" and row[0].isdigit():
                    products = []
                    prods = row[2].split(";")
                    for p in prods:
                        if p.strip():
                            name, qty, price = p.strip().split(",")
                            products.append({"name": name, "qty": int(qty), "price": float(price)})
                    orders.append({
                        "id": int(row[0]),
                        "client_id": int(row[1]),
                        "products": products
                    })
    refresh_clients()
    refresh_orders()
    messagebox.showinfo("Импорт", "Данные успешно импортированы")

# Визуализация
def show_sales_dynamics():
    sales_per_client = defaultdict(float)
    for o in orders:
        total = sum(p["qty"] * p["price"] for p in o["products"])
        sales_per_client[o["client_id"]] += total

    clients_names = [c["name"] for c in clients if c["id"] in sales_per_client]
    sales_values = [sales_per_client[c["id"]] for c in clients if c["id"] in sales_per_client]

    fig = plt.Figure(figsize=(6,4))
    ax = fig.add_subplot(111)
    ax.bar(clients_names, sales_values)
    ax.set_title("Объем продаж по клиентам")
    ax.set_ylabel("Сумма продаж")

    chart_win = tk.Toplevel(root)
    chart_win.title("Визуализация - продажи")
    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas.get_tk_widget().pack()
    canvas.draw()

# GUI
root = tk.Tk()
root.title("Менеджер интернет-магазина")

notebook = ttk.Notebook(root)
frame_clients = ttk.Frame(notebook)
frame_orders = ttk.Frame(notebook)
frame_analysis = ttk.Frame(notebook)

notebook.add(frame_clients, text="Клиенты")
notebook.add(frame_orders, text="Заказы")
notebook.add(frame_analysis, text="Аналитика")
notebook.pack(expand=True, fill="both")

# Клиенты
tree_clients = ttk.Treeview(frame_clients, columns=("id", "name", "email", "phone"), show="headings")
for col in ("id", "name&quot", "email", "phone"):
    tree_clients.heading(col, text=col)
tree_clients.pack(fill="both", expand=True)

clients_frame = ttk.Frame(frame_clients)
clients_frame.pack(pady=10)

ttk.Label(clients_frame, text="Имя").grid(row=0, column=0)
e_name = ttk.Entry(clients_frame)
e_name.grid(row=0, column=1)

ttk.Label(clients_frame, text="Email").grid(row=1, column=0)
e_email = ttk.Entry(clients_frame)
e_email.grid(row=1, column=1)

ttk.Label(clients_frame, text="Телефон").grid(row=2, column=0)
e_phone = ttk.Entry(clients_frame)
e_phone.grid(row=2, column=1)

def on_add_client():
    name = e_name.get().strip()
    email = e_email.get().strip()
    phone = e_phone.get().strip()
    if not name or not email:
        messagebox.showerror("Ошибка", "Имя и Email обязательны")
        return
    add_client(name, email, phone)
    e_name.delete(0, tk.END)
    e_email.delete(0, tk.END)
    e_phone.delete(0, tk.END)

ttk.Button(clients_frame, text="Добавить клиента", command=on_add_client).grid(row=3, column=0, columnspan=2, pady=5)

# Заказы
tree_orders = ttk.Treeview(frame_orders, columns=("id", "client_id", "products"), show="headings")
tree_orders.heading("id", text="ID")
tree_orders.heading("client_id", text="ID Клиента")
tree_orders.heading("products", text="Товары (название × количество)")
tree_orders.pack(fill="both", expand=True)

orders_frame = ttk.Frame(frame_orders)
orders_frame.pack(pady=10)

ttk.Label(orders_frame, text="ID Клиента").grid(row=0, column=0)
e_client_id = ttk.Entry(orders_frame)
e_client_id.grid(row=0, column=1)

ttk.Label(orders_frame, text="Товары (название,кол-во,цена; ...)").grid(row=1, column=0)
e_products = ttk.Entry(orders_frame, width=50)
e_products.grid(row=1, column=1)

def on_add_order():
    client_id = e_client_id.get().strip()
    products = e_products.get().strip()
    if not client_id.isdigit() or not products:
        messagebox.showerror("Ошибка", "Неверные данные")
        return
    if int(client_id) not in [c["id"] for c in clients]:
        messagebox.showerror("Ошибка", "Клиент с таким ID не найден")
        return
    try:
        add_order(client_id, products)
    except Exception as e:
        messagebox.showerror("Ошибка", "Ошибка при добавлении заказа: " + str(e))
    e_client_id.delete(0, tk.END)
    e_products.delete(0, tk.END)

ttk.Button(orders_frame, text="Добавить заказ", command=on_add_order).grid(row=2, column=0, columnspan=2, pady=5)

# Фильтрация
filter_frame = ttk.Frame(frame_orders)
filter_frame.pack(pady=5)

ttk.Label(filter_frame, text="Фильтр по ID клиента").grid(row=0, column=0)
e_filter_client = ttk.Entry(filter_frame, width=10)
e_filter_client.grid(row=0, column=1)

ttk.Label(filter_frame, text="Сортировка").grid(row=0, column=2)
sort_combo = ttk.Combobox(filter_frame, values=["без сортировки", "id", "client_id"])
sort_combo.current(0)
sort_combo.grid(row=0, column=3)

def on_filter_sort():
    client_filter = e_filter_client.get()
    if client_filter != "" and not client_filter.isdigit():
        messagebox.showerror("Ошибка", "ID клиента должен быть числом")
        return
    filt = client_filter if client_filter else None
    sort = sort_combo.get()
    if sort == "бз сортировки":
        sort = None
    refresh_orders(filter_client=filt, sort_by=sort)

ttk.Button(filter_frame, text="Применить", command=on_filter_sort).grid(row=0, column=4, padx=5)

ttk.Button(frame_analysis, text="Показать динамику продаж", command=show_sales_dynamics).pack(pady=20)

# Меню
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Файл", menu=file_menu)
file_menu.add_command(label="Импорт данных", command=import_data)
file_menu.add_command(label="Экспорт данных", command=export_data)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)

refresh_clients()
refresh_orders()

root.mainloop()
