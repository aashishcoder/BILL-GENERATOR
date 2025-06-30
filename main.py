import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
from invoice_generator import generate_pdf_invoice
from utils import save_invoice_data
from datetime import datetime

CUSTOMER_FILE = "data/customers.json"

def load_customers():
    if os.path.exists(CUSTOMER_FILE):
        with open(CUSTOMER_FILE, "r") as f:
            return json.load(f)
    return []

from datetime import datetime

def search_invoices():
    search_win = tk.Toplevel()
    search_win.title("Search Invoices")
    search_win.geometry("700x500")

    # UI Elements
    tk.Label(search_win, text="Search by Customer / Invoice No / Date (YYYY-MM-DD):").pack(pady=5)
    search_entry = tk.Entry(search_win, width=50)
    search_entry.pack(pady=5)

    tk.Label(search_win, text="From Date (YYYY-MM-DD):").pack()
    from_date_entry = tk.Entry(search_win)
    from_date_entry.pack()

    tk.Label(search_win, text="To Date (YYYY-MM-DD):").pack()
    to_date_entry = tk.Entry(search_win)
    to_date_entry.pack()

    result_text = tk.Text(search_win, height=20, width=85)
    result_text.pack(pady=10)

    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None

    def do_search():
        term = search_entry.get().strip().lower()
        from_date = parse_date(from_date_entry.get().strip())
        to_date = parse_date(to_date_entry.get().strip())

        folder = "data/invoices"
        results = []

        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".json"):
                    with open(os.path.join(folder, filename), "r") as f:
                        invoice = json.load(f)
                        inv_date = parse_date(invoice.get("date", ""))
                        matches_term = (
                            term in invoice.get("customer", "").lower() or
                            term in invoice.get("invoice_no", "").lower() or
                            term in invoice.get("date", "")
                        )
                        matches_date_range = True
                        if from_date and inv_date:
                            matches_date_range = inv_date >= from_date
                        if to_date and inv_date:
                            matches_date_range = matches_date_range and inv_date <= to_date

                        if matches_term and matches_date_range:
                            results.append(invoice)

        result_text.delete("1.0", tk.END)

        if results:
            results.sort(key=lambda x: x.get("date", ""), reverse=True)  # Sort by date descending
            for inv in results:
                total_amt = sum(item.get("total", 0) for item in inv["items"])
                result_text.insert(tk.END, f"Invoice: {inv['invoice_no']} | Customer: {inv['customer']} | Date: {inv['date']} | Total: ₹{total_amt:.2f}\n")
        else:
            result_text.insert(tk.END, "No matching invoices found.")

    # Buttons
    tk.Button(search_win, text="Search", command=do_search).pack(pady=5)
    tk.Button(search_win, text="Close", command=search_win.destroy).pack(pady=5)



def save_customer(name):
    customers = load_customers()
    if name and name not in customers:
        customers.append(name)
        with open(CUSTOMER_FILE, "w") as f:
            json.dump(customers, f, indent=4)
            
def preview_invoice(data, confirm_callback):
    preview_win = tk.Toplevel()
    preview_win.title("Invoice Preview")
    preview_win.geometry("600x400")

    # Convert line items to a text block
    items_text = "\n".join([f"{item['description']} - Qty: {item['quantity']} @ ₹{item['rate']} = ₹{item['total']}" for item in data['items']])
    total_amt = sum([item['total'] for item in data['items']])

    preview_text = f"""
    Company: XYZ Pvt. Ltd.
    Customer: {data['customer']}
    Date: {data['date']}

    Items:
    {items_text}

    Total Amount: ₹{total_amt:.2f}
    """

    label = tk.Label(preview_win, text=preview_text, justify='left', font=("Courier", 10))
    label.pack(padx=10, pady=10)

    # Confirm button
    tk.Button(preview_win, text="Confirm & Generate PDF", command=lambda: [preview_win.destroy(), confirm_callback()]).pack(pady=5)
    tk.Button(preview_win, text="Cancel", command=preview_win.destroy).pack()

def create_invoice():
    invoice_no = invoice_entry.get().strip()
    customer = customer_combobox.get().strip()

    if not invoice_no or not customer:
        messagebox.showerror("Error", "Please fill in Invoice No and Customer Name")
        return

    items = []

    for row in item_rows:
        desc = row[0].get().strip()
        hsn = row[1].get().strip()
        try:
            qty = float(row[2].get().strip())
            rate = float(row[3].get().strip())
        except ValueError:
            messagebox.showerror("Error", "Quantity and Rate must be numbers")
            return

        if not desc or not hsn:
            messagebox.showerror("Error", "Please fill in all item details")
            return

        total = qty * rate
        items.append({
            "description": desc,
            "hsn": hsn,
            "quantity": qty,
            "rate": rate,
            "total": total
        })
        if not items:
            messagebox.showerror("Error", "No valid item rows found. Please enter at least one item.")
            return


    date = datetime.now().strftime("%Y-%m-%d")

    data = {
        "invoice_no": invoice_no,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "customer": customer,
        "items": items
    }

    # ➤ Preview first
    def proceed_with_generation():
        filepath = generate_pdf_invoice(data)
        save_invoice_data(data, f"data/invoices/{invoice_no}.json")

        save_customer(customer)
        messagebox.showinfo("Success", f"Invoice {invoice_no} created successfully!")

    preview_invoice(data, proceed_with_generation)

def add_item_row():
    row_widgets = []
    row_index = len(item_rows) + 2

    for i, placeholder in enumerate(["Description", "HSN", "Qty", "Rate"]):
        entry = tk.Entry(root)
        entry.grid(row=row_index, column=i, padx=5, pady=5)
        row_widgets.append(entry)

    # Delete button for the row
    def delete_row():
        if messagebox.askyesno("Delete Item", "Are you sure you want to delete this item row?"):
            for widget in row_widgets:
                widget.destroy()
            delete_button.destroy()
            item_rows.remove(row_widgets)

    delete_button = tk.Button(root, text="❌", command=delete_row)
    delete_button.grid(row=row_index, column=4, padx=5, pady=5)
    row_widgets.append(delete_button)

    item_rows.append(row_widgets)


root = tk.Tk()
root.title("Billing Software")

# Invoice & Customer Details
customer_list = load_customers()

invoice_label = tk.Label(root, text="Invoice No:")
invoice_label.grid(row=0, column=0, padx=5, pady=5)
invoice_entry = tk.Entry(root)
invoice_entry.grid(row=0, column=1, padx=5, pady=5)

customer_label = tk.Label(root, text="Customer:")
customer_label.grid(row=0, column=2, padx=5, pady=5)
customer_combobox = ttk.Combobox(root, values=customer_list)
customer_combobox.grid(row=0, column=3, padx=5, pady=5)
customer_combobox.set("")

# Table Headers
headers = ["Description", "HSN", "Qty", "Rate"]
for i, header in enumerate(headers):
    label = tk.Label(root, text=header)
    label.grid(row=1, column=i, padx=5, pady=5)

# Item Rows
item_rows = []
add_item_row()  # Add initial row

# Buttons
add_button = tk.Button(root, text="+ Add Item", command=add_item_row)
add_button.grid(row=100, column=0, padx=5, pady=10)

generate_button = tk.Button(root, text="Generate Invoice", command=create_invoice)
generate_button.grid(row=100, column=1, columnspan=2, padx=5, pady=10)

search_button = tk.Button(root, text="Search Invoices", command=search_invoices)
search_button.grid(row=100, column=3, padx=5, pady=10)

root.mainloop()

