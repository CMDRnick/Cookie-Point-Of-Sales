import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import pandas as pd

print("Starting The Cookie Palace POS System...")

# In-memory data storage
items = []
transactions = []
current_transaction = []

def update_time(label):
    """Update the displayed time every second."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=now)
    label.after(1000, update_time, label)

def list_items(tree):
    """List all items available in the shop."""
    for row in tree.get_children():
        tree.delete(row)
    for idx, item in enumerate(items, start=1):
        tree.insert("", "end", values=(idx, item["name"], f"RM {item['price']:.2f}", item["quantity"]))

def add_item(name_entry, price_entry, quantity_entry, tree):
    """Add a new item to the in-memory storage."""
    name = name_entry.get().strip()  # Strip leading/trailing whitespace
    price_str = price_entry.get().strip()  # Get price input as string
    quantity_str = quantity_entry.get().strip()  # Get quantity input as string
    
    # Check if all fields are not empty
    if not name or not price_str or not quantity_str:
        messagebox.showerror("Error", "All fields must be filled out.")
        return
    
    try:
        # Check if the price is a valid number (float)
        price = float(price_str)
        if price <= 0:
            raise ValueError("Price must be greater than 0.")
        
        # Check if the quantity is a valid integer
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        
        # Append the new item to the inventory
        items.append({"name": name, "price": price, "quantity": quantity, "sold": 0})
        messagebox.showinfo("Success", f"Item '{name}' added successfully.")
        
        # Clear the entry fields
        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        
        # Update the item list in the Treeview
        list_items(tree)

    except ValueError as e:
        messagebox.showerror("Error", str(e))

def add_to_cart(item_id_entry, quantity_entry, cart_tree, subtotal_label):
    """Add an item to the current transaction."""
    try:
        item_id = int(item_id_entry.get()) - 1
        quantity = int(quantity_entry.get())
        if 0 <= item_id < len(items) and 0 < quantity <= items[item_id]["quantity"]:
            item = items[item_id]
            current_transaction.append({"name": item["name"], "price": item["price"], "quantity": quantity})
            item["quantity"] -= quantity
            update_cart_display(cart_tree)
            update_subtotal(subtotal_label)
        else:
            messagebox.showerror("Error", "Invalid quantity or item ID.")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter numeric values.")

def update_cart_display(cart_tree):
    """Update the cart display."""
    for row in cart_tree.get_children():
        cart_tree.delete(row)
    for idx, item in enumerate(current_transaction, start=1):
        cart_tree.insert("", "end", values=(idx, item["name"], item["quantity"], f"RM {item['price']:.2f}"))

def update_subtotal(subtotal_label):
    """Update the subtotal label."""
    subtotal = sum(item["price"] * item["quantity"] for item in current_transaction)
    subtotal_label.config(text=f"Subtotal: RM {subtotal:.2f}")

def cancel_transaction(cart_tree, subtotal_label):
    """Cancel the current transaction."""
    global current_transaction
    for item in current_transaction:
        for inventory_item in items:
            if inventory_item["name"] == item["name"]:
                inventory_item["quantity"] += item["quantity"]
    current_transaction = []
    update_cart_display(cart_tree)
    update_subtotal(subtotal_label)
    messagebox.showinfo("Transaction Canceled", "The transaction has been canceled.")

def process_transaction(payment_method, amount_entry, cart_tree, subtotal_label):
    """Process the current transaction."""
    if not current_transaction:
        messagebox.showerror("Error", "The cart is empty. Add items to the cart first.")
        return
    subtotal = sum(item["price"] * item["quantity"] for item in current_transaction)
    if payment_method == "Cash":
        try:
            cash = float(amount_entry.get())
            if cash >= subtotal:
                change = cash - subtotal
                finalize_transaction(cart_tree, subtotal_label)
                messagebox.showinfo("Transaction Completed", f"Payment successful! Change: RM {change:.2f}")
            else:
                messagebox.showerror("Error", "Insufficient cash amount.")
        except ValueError:
            messagebox.showerror("Error", "Invalid cash amount.")
    elif payment_method in ["Master/Visa", "QR Payment"]:
        finalize_transaction(cart_tree, subtotal_label)
        messagebox.showinfo("Transaction Completed", f"Payment successful via {payment_method}.")
    else:
        messagebox.showerror("Error", "Invalid payment method.")

def finalize_transaction(cart_tree, subtotal_label):
    """Finalize the transaction by updating inventory and storing the transaction."""
    global current_transaction
    for item in current_transaction:
        for inventory_item in items:
            if inventory_item["name"] == item["name"]:
                inventory_item["sold"] += item["quantity"]
    transactions.append({"items": current_transaction, "date": datetime.now()})
    current_transaction = []
    update_cart_display(cart_tree)
    update_subtotal(subtotal_label)

def generate_sales_report():
    """Generate a sales report in Excel format."""
    if transactions:
        report_data = []
        for transaction in transactions:
            for item in transaction["items"]:
                report_data.append({
                    "Item Name": item["name"],
                    "Quantity": item["quantity"],
                    "Total Price": item["price"] * item["quantity"],
                    "Date": transaction["date"].strftime("%Y-%m-%d %H:%M:%S")
                })
        df = pd.DataFrame(report_data)
        filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Report Generated", f"Sales report saved as {filename}.")
    else:
        messagebox.showinfo("No Transactions", "No transactions to report.")

def remove_from_cart(item_id_entry, cart_tree, subtotal_label):
    """Remove an item from the cart."""
    try:
        item_id = int(item_id_entry.get()) - 1
        if 0 <= item_id < len(current_transaction):
            item = current_transaction.pop(item_id)
            for inventory_item in items:
                if inventory_item["name"] == item["name"]:
                    inventory_item["quantity"] += item["quantity"]
            update_cart_display(cart_tree)
            update_subtotal(subtotal_label)
        else:
            messagebox.showerror("Error", "Invalid item ID.")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter a numeric item ID.")

def main():
    """Main function to run the tkinter UI."""
    root = tk.Tk()
    root.title("The Cookie Palace - Point Of Sales System")
    root.geometry("900x700")
    root.configure(bg="#F5F5DC")  # Classy cream background

    # Header
    header_frame = tk.Frame(root, bg="#F5F5DC")
    header_frame.pack(fill="x")

    header = tk.Label(header_frame, text="The Cookie Palace POS", font=("Arial", 24, "bold"), bg="#F5F5DC", fg="#8B4513")
    header.pack(side="left", padx=10)

    time_label = tk.Label(header_frame, font=("Arial", 12), bg="#F5F5DC", fg="#8B4513")
    time_label.pack(side="right", padx=10)
    update_time(time_label)

    # Tabs
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Tab 1: List Items
    tab_list = ttk.Frame(tab_control)
    tab_control.add(tab_list, text="List Items")

    tree = ttk.Treeview(tab_list, columns=("ID", "Name", "Price", "Quantity"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Price", text="Price")
    tree.heading("Quantity", text="Quantity")
    tree.column("ID", width=50)
    tree.column("Name", width=200)
    tree.column("Price", width=100)
    tree.column("Quantity", width=100)
    tree.pack(fill="both", expand=True, pady=10)

    list_items(tree)

    # Tab 2: Add Item
    tab_add = ttk.Frame(tab_control)
    tab_control.add(tab_add, text="Add Item")

    tk.Label(tab_add, text="Item Name:", bg="#F5F5DC", fg="#8B4513").pack(pady=5)
    name_entry = tk.Entry(tab_add)
    name_entry.pack(pady=5)

    tk.Label(tab_add, text="Item Price (RM):", bg="#F5F5DC", fg="#8B4513").pack(pady=5)
    price_entry = tk.Entry(tab_add)
    price_entry.pack(pady=5)

    tk.Label(tab_add, text="Item Quantity:", bg="#F5F5DC", fg="#8B4513").pack(pady=5)
    quantity_entry = tk.Entry(tab_add)
    quantity_entry.pack(pady=5)

    tk.Button(tab_add, text="Add Item", command=lambda: add_item(name_entry, price_entry, quantity_entry, tree), bg="#8B4513", fg="white").pack(pady=10)

    # Tab 3: Transaction
    tab_transaction = ttk.Frame(tab_control)
    tab_control.add(tab_transaction, text="Transaction")

    tk.Label(tab_transaction, text="Transaction Tab", font=("Arial", 14, "bold"), bg="#F5F5DC", fg="#8B4513").pack(pady=10)

    cart_tree = ttk.Treeview(tab_transaction, columns=("ID", "Name", "Quantity", "Price"), show="headings")
    cart_tree.heading("ID", text="ID")
    cart_tree.heading("Name", text="Name")
    cart_tree.heading("Quantity", text="Quantity")
    cart_tree.heading("Price", text="Price")
    cart_tree.column("ID", width=50)
    cart_tree.column("Name", width=150)
    cart_tree.column("Quantity", width=100)
    cart_tree.column("Price", width=100)
    cart_tree.pack(fill="both", expand=True, pady=10)

    subtotal_label = tk.Label(tab_transaction, text="Subtotal: RM 0.00", font=("Arial", 12), bg="#F5F5DC", fg="#8B4513")
    subtotal_label.pack(pady=10)

    payment_frame = tk.Frame(tab_transaction, bg="#F5F5DC")
    payment_frame.pack(fill="x", pady=10)

    tk.Label(payment_frame, text="Payment Method:", bg="#F5F5DC", fg="#8B4513").grid(row=0, column=0, padx=10)
    payment_method_var = tk.StringVar(value="Cash")
    payment_methods = ["Cash", "Master/Visa", "QR Payment"]
    payment_menu = ttk.OptionMenu(payment_frame, payment_method_var, *payment_methods)
    payment_menu.grid(row=0, column=1, padx=10)

    tk.Label(payment_frame, text="Amount:", bg="#F5F5DC", fg="#8B4513").grid(row=0, column=2, padx=10)
    amount_entry = tk.Entry(payment_frame)
    amount_entry.grid(row=0, column=3, padx=10)

    btn_frame = tk.Frame(tab_transaction, bg="#F5F5DC")
    btn_frame.pack(fill="x", pady=10)

    tk.Button(btn_frame, text="Add to Cart", command=lambda: add_to_cart(item_id_entry, quantity_entry, cart_tree, subtotal_label), bg="#8B4513", fg="white").grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Remove Item", command=lambda: remove_from_cart(item_id_entry, cart_tree, subtotal_label), bg="#8B4513", fg="white").grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Cancel Transaction", command=lambda: cancel_transaction(cart_tree, subtotal_label), bg="#8B4513", fg="white").grid(row=0, column=2, padx=10)
    tk.Button(btn_frame, text="Complete Transaction", command=lambda: process_transaction(payment_method_var.get(), amount_entry, cart_tree, subtotal_label), bg="#8B4513", fg="white").grid(row=0, column=3, padx=10)

    # Item selection frame
    item_select_frame = tk.Frame(tab_transaction, bg="#F5F5DC")
    item_select_frame.pack(fill="x", pady=10)

    tk.Label(item_select_frame, text="Item ID:", bg="#F5F5DC", fg="#8B4513").grid(row=0, column=0, padx=10)
    item_id_entry = tk.Entry(item_select_frame)
    item_id_entry.grid(row=0, column=1, padx=10)

    tk.Label(item_select_frame, text="Quantity:", bg="#F5F5DC", fg="#8B4513").grid(row=0, column=2, padx=10)
    quantity_entry = tk.Entry(item_select_frame)
    quantity_entry.grid(row=0, column=3, padx=10)

    # Tab 4: Sales Report
    tab_sales_report = ttk.Frame(tab_control)
    tab_control.add(tab_sales_report, text="Sales Report")

    tk.Button(tab_sales_report, text="Generate Sales Report", command=generate_sales_report, bg="#8B4513", fg="white").pack(pady=20)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()