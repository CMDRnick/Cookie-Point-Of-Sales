import tkinter as tk
from tkinter import messagebox, ttk

# In-memory data storage
items = []
transactions = []

def list_items(tree):
    """List all items available in the shop."""
    for row in tree.get_children():
        tree.delete(row)
    for idx, item in enumerate(items, start=1):
        tree.insert("", "end", values=(idx, item["name"], f"RM {item['price']:.2f}"))

def add_item(name_entry, price_entry, tree):
    """Add a new item to the in-memory storage."""
    name = name_entry.get()
    try:
        price = float(price_entry.get())
        items.append({"name": name, "price": price})
        messagebox.showinfo("Success", f"Item '{name}' added successfully.")
        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        list_items(tree)
    except ValueError:
        messagebox.showerror("Error", "Invalid price. Please enter a numeric value.")

def process_transaction(item_id_entry, quantity_entry):
    """Process a transaction."""
    try:
        item_id = int(item_id_entry.get()) - 1
        if 0 <= item_id < len(items):
            quantity = int(quantity_entry.get())
            total_price = items[item_id]["price"] * quantity
            transactions.append({"item": items[item_id]["name"], "quantity": quantity, "total_price": total_price})
            messagebox.showinfo("Success", f"Transaction successful! Total: RM {total_price:.2f}")
            item_id_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid item ID.")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter numeric values.")

def main():
    """Main function to run the tkinter UI."""
    root = tk.Tk()
    root.title("The Cookie Palace - Point Of Sales System")
    root.geometry("600x500")
    root.configure(bg="#FFFDD0")  # Cream color background

    # Header
    header = tk.Label(root, text="The Cookie Palace POS", font=("Arial", 18, "bold"), bg="#FFFDD0", fg="#A0522D")
    header.pack(pady=10)

    # Tabs
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Tab 1: List Items
    tab_list = ttk.Frame(tab_control)
    tab_control.add(tab_list, text="List Items")

    tree = ttk.Treeview(tab_list, columns=("ID", "Name", "Price"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Price", text="Price")
    tree.column("ID", width=50)
    tree.column("Name", width=200)
    tree.column("Price", width=100)
    tree.pack(fill="both", expand=True, pady=10)

    list_items(tree)

    # Tab 2: Add Item
    tab_add = ttk.Frame(tab_control)
    tab_control.add(tab_add, text="Add Item")

    tk.Label(tab_add, text="Item Name:", bg="#FFFDD0", fg="#A0522D").pack(pady=5)
    name_entry = tk.Entry(tab_add)
    name_entry.pack(pady=5)

    tk.Label(tab_add, text="Item Price (RM):", bg="#FFFDD0", fg="#A0522D").pack(pady=5)
    price_entry = tk.Entry(tab_add)
    price_entry.pack(pady=5)

    add_button = tk.Button(tab_add, text="Add Item", bg="#F5DEB3", fg="#A0522D", command=lambda: add_item(name_entry, price_entry, tree))
    add_button.pack(pady=10)

    # Tab 3: Process Transaction
    tab_transaction = ttk.Frame(tab_control)
    tab_control.add(tab_transaction, text="Process Transaction")

    tk.Label(tab_transaction, text="Item ID:", bg="#FFFDD0", fg="#A0522D").pack(pady=5)
    item_id_entry = tk.Entry(tab_transaction)
    item_id_entry.pack(pady=5)

    tk.Label(tab_transaction, text="Quantity:", bg="#FFFDD0", fg="#A0522D").pack(pady=5)
    quantity_entry = tk.Entry(tab_transaction)
    quantity_entry.pack(pady=5)

    transaction_button = tk.Button(tab_transaction, text="Process Transaction", bg="#F5DEB3", fg="#A0522D", command=lambda: process_transaction(item_id_entry, quantity_entry))
    transaction_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
