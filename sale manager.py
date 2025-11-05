import tkinter as tk
from tkinter import ttk, messagebox
import csv, os, random

SALES_FILE = "sales_data.csv"
CUSTOMERS_FILE = "customers.csv"
PRODUCTS_FILE = "products.csv"

# --------- DATA MANAGEMENT ---------
def save_sale(product, quantity, price):
    total = quantity * price
    with open(SALES_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([product, quantity, price, total])

def load_sales():
    if not os.path.exists(SALES_FILE):
        return []
    with open(SALES_FILE, mode="r") as file:
        return list(csv.reader(file))

def calculate_total():
    sales = load_sales()
    return sum(float(s[3]) for s in sales) if sales else 0

# --------- CUSTOMERS ---------
def save_customer(name):
    with open(CUSTOMERS_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name])

def load_customers():
    if not os.path.exists(CUSTOMERS_FILE):
        return []
    with open(CUSTOMERS_FILE, mode="r") as file:
        return [c[0] for c in csv.reader(file)]

# --------- PRODUCTS ---------
def save_product(name, price):
    with open(PRODUCTS_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, price])

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, mode="r") as file:
        return list(csv.reader(file))

# --------- CHATBOT LOGIC ---------
def bot_reply(msg):
    msg = msg.lower().strip()

    if "hello" in msg or "hi" in msg:
        return random.choice(["Hey there! 😊", "Hello boss! Ready to record some sales?", "Hi! What are we selling today?"])
    
    elif "add sale" in msg:
        try:
            parts = msg.split()
            # e.g. "add sale apple 5 200"
            product = parts[2]
            quantity = int(parts[3])
            price = float(parts[4])
            save_sale(product, quantity, price)
            refresh_sales()
            return f"✅ Added {quantity} {product}(s) at {price:.2f} CFA each."
        except Exception:
            return "⚠️ Please say: add sale [product] [quantity] [price]"
    
    elif "total" in msg:
        total = calculate_total()
        return f"💰 Total sales so far: {total:.2f} CFA"
    
    elif "show sales" in msg or "view sales" in msg:
        refresh_sales()
        return "📊 Sales list refreshed!"
    
    elif "add customer" in msg:
        try:
            name = msg.replace("add customer", "").strip().capitalize()
            if name:
                save_customer(name)
                refresh_customers()
                return f"👤 Customer '{name}' added successfully."
            else:
                return "⚠️ Please provide a customer name."
        except:
            return "❌ Error adding customer."
    
    elif "add product" in msg:
        try:
            # e.g. "add product rice 400"
            parts = msg.split()
            name = parts[2]
            price = float(parts[3])
            save_product(name, price)
            refresh_products()
            return f"📦 Product '{name}' added at {price:.2f} CFA."
        except Exception:
            return "⚠️ Please say: add product [name] [price]"
    
    elif "thank" in msg:
        return "You're welcome! 😄"
    elif "clear" in msg:
        chat_box.config(state="normal")
        chat_box.delete("1.0", tk.END)
        chat_box.config(state="disabled")
        return "Chat cleared 🧹"
    elif "bye" in msg:
        root.destroy()
        return "Goodbye 👋"
    else:
        return random.choice([
            "I'm not sure I understand 🤔. Try 'add sale apple 5 200'",
            "I can help with sales, products, and customers 💼",
            "Try 'show sales' or 'total' to begin!"
        ])

# --------- SEND MESSAGE ---------
def send_message():
    user_msg = user_input.get().strip()
    if not user_msg:
        return
    insert_message(f"You: {user_msg}\n", "user")
    user_input.delete(0, tk.END)
    response = bot_reply(user_msg)
    insert_message(f"Bot: {response}\n", "bot")

def insert_message(msg, tag):
    chat_box.config(state="normal")
    chat_box.insert(tk.END, msg, tag)
    chat_box.config(state="disabled")
    chat_box.see(tk.END)

# --------- USER INTERFACE ---------
root = tk.Tk()
root.title("🤖 AI Sales Management Bot (CFA)")
root.geometry("1100x600")
root.config(bg="#f5f7fa")

# ---- Left Side: Chat ----
chat_frame = tk.Frame(root, bg="#f5f7fa", width=400)
chat_frame.pack(side="left", fill="both", padx=10, pady=10)

tk.Label(chat_frame, text="💬 Chat with your Sales Bot", font=("Arial", 14, "bold"), bg="#f5f7fa").pack()

chat_box = tk.Text(chat_frame, wrap="word", state="disabled", height=20, bg="white", font=("Arial", 11))
chat_box.pack(pady=5, fill="both", expand=True)

chat_box.tag_config("user", foreground="#2c3e50", font=("Arial", 11, "bold"))
chat_box.tag_config("bot", foreground="#0a9396", font=("Arial", 11, "italic"))

user_input = tk.Entry(chat_frame, width=40, font=("Arial", 12))
user_input.pack(side="left", pady=10, padx=(0, 5), ipady=5)

tk.Button(chat_frame, text="Send", command=send_message, bg="#0078D4", fg="white", font=("Arial", 11), width=10).pack(side="right", pady=10)

insert_message("Bot: Hello! I’m your AI Sales Manager 🤖\nTry 'add sale apple 5 200' to begin.\n\n", "bot")

# ---- Right Side: Tables ----
right_frame = tk.Frame(root, bg="#f5f7fa")
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# --- Sales Table ---
tk.Label(right_frame, text="📊 Sales Records", font=("Arial", 14, "bold"), bg="#f5f7fa").pack(pady=5)
sales_columns = ("Product", "Quantity", "Price (CFA)", "Total (CFA)")
sales_table = ttk.Treeview(right_frame, columns=sales_columns, show="headings", height=10)
for col in sales_columns:
    sales_table.heading(col, text=col)
    sales_table.column(col, width=120)
sales_table.pack(fill="x", pady=5)

def refresh_sales():
    for row in sales_table.get_children():
        sales_table.delete(row)
    for s in load_sales():
        sales_table.insert("", tk.END, values=s)

# --- Customer Table ---
tk.Label(right_frame, text="👥 Customer List", font=("Arial", 14, "bold"), bg="#f5f7fa").pack(pady=5)
customer_table = ttk.Treeview(right_frame, columns=("Customer Name",), show="headings", height=5)
customer_table.heading("Customer Name", text="Customer Name")
customer_table.column("Customer Name", width=250)
customer_table.pack(fill="x", pady=5)

def refresh_customers():
    for row in customer_table.get_children():
        customer_table.delete(row)
    for c in load_customers():
        customer_table.insert("", tk.END, values=(c,))

# --- Product Table ---
tk.Label(right_frame, text="📦 Product Inventory", font=("Arial", 14, "bold"), bg="#f5f7fa").pack(pady=5)
product_table = ttk.Treeview(right_frame, columns=("Product", "Price (CFA)"), show="headings", height=5)
for col in ("Product", "Price (CFA)"):
    product_table.heading(col, text=col)
    product_table.column(col, width=150)
product_table.pack(fill="x", pady=5)

def refresh_products():
    for row in product_table.get_children():
        product_table.delete(row)
    for p in load_products():
        product_table.insert("", tk.END, values=p)

# Initial load
refresh_sales()
refresh_customers()
refresh_products()

root.mainloop()
