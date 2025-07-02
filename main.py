import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
from invoice_generator import generate_pdf_invoice
from utils import save_invoice_data
from datetime import datetime
import platform

CUSTOMER_FILE = "data/customers.json"
ITEM_FILE = "data/items.json"

def load_customers():
    if os.path.exists(CUSTOMER_FILE):
        with open(CUSTOMER_FILE, "r") as f:
            return json.load(f)
    return []

def load_items():
    if os.path.exists(ITEM_FILE):
        with open(ITEM_FILE, "r") as f:
            return json.load(f)
    return []

def save_item(description, hsn, unit):
    items = load_items()
    if not any(i["description"] == description for i in items):
        items.append({"description": description, "hsn": hsn, "unit": unit})
        with open(ITEM_FILE, "w") as f:
            json.dump(items, f, indent=4)

def save_customer(customer_data):
    customers = load_customers()
    for i, c in enumerate(customers):
        if c["name"] == customer_data["name"]:
            customers[i] = customer_data
            break
    else:
        customers.append(customer_data)
    with open(CUSTOMER_FILE, "w") as f:
        json.dump(customers, f, indent=4)

def on_customer_selected(event):
    selected_name = customer_combobox.get()
    for c in load_customers():
        if c["name"] == selected_name:
            bill_address_entry.delete("1.0", tk.END)
            bill_address_entry.insert(tk.END, c.get("bill_to", ""))
            ship_address_entry.delete("1.0", tk.END)
            ship_address_entry.insert(tk.END, c.get("ship_to", ""))
            mobile_entry.delete(0, tk.END)
            mobile_entry.insert(0, c.get("mobile", ""))
            gstin_entry.delete(0, tk.END)
            gstin_entry.insert(0, c.get("gstin", ""))
            pan_entry.delete(0, tk.END)
            pan_entry.insert(0, c.get("pan", ""))
            state_entry.delete(0, tk.END)
            state_entry.insert(0, c.get("state", ""))
            break

def open_add_item_dialog():
    win = tk.Toplevel()
    win.title("Add New Item")
    win.geometry("300x200")

    tk.Label(win, text="Description:").pack(pady=2)
    desc_entry = tk.Entry(win)
    desc_entry.pack(pady=2)

    tk.Label(win, text="HSN Code:").pack(pady=2)
    hsn_entry = tk.Entry(win)
    hsn_entry.pack(pady=2)

    tk.Label(win, text="Unit (e.g., KGS, PCS):").pack(pady=2)
    unit_entry = tk.Entry(win)
    unit_entry.pack(pady=2)

    def save():
        desc = desc_entry.get().strip()
        hsn = hsn_entry.get().strip()
        unit = unit_entry.get().strip()
        if not desc or not hsn or not unit:
            messagebox.showerror("Error", "Please fill all fields")
            return
        save_item(desc, hsn, unit)
        win.destroy()
        messagebox.showinfo("Success", "Item saved successfully")

    tk.Button(win, text="Save", command=save).pack(pady=10)

def add_item_row():
    row_widgets = []
    row_index = len(item_rows) + 1

    item_options = [i["description"] for i in load_items()]
    desc_var = tk.StringVar()
    desc_cb = ttk.Combobox(item_frame_inner, values=item_options, textvariable=desc_var, width=25)
    desc_cb.grid(row=row_index, column=0, padx=5, pady=3)

    hsn_entry = tk.Entry(item_frame_inner, width=10)
    hsn_entry.grid(row=row_index, column=1, padx=5, pady=3)

    qty_entry = tk.Entry(item_frame_inner, width=8)
    qty_entry.grid(row=row_index, column=2, padx=5, pady=3)

    rate_entry = tk.Entry(item_frame_inner, width=10)
    rate_entry.grid(row=row_index, column=3, padx=5, pady=3)

    unit_entry = tk.Entry(item_frame_inner, width=10)
    unit_entry.grid(row=row_index, column=4, padx=5, pady=3)

    def on_item_selected(event):
        selected = desc_var.get()
        for item in load_items():
            if item["description"] == selected:
                hsn_entry.delete(0, tk.END)
                hsn_entry.insert(0, item["hsn"])
                unit_entry.delete(0, tk.END)
                unit_entry.insert(0, item.get("unit", ""))

    desc_cb.bind("<<ComboboxSelected>>", on_item_selected)

    delete_button = tk.Button(item_frame_inner, text="❌", command=lambda: delete_row(row_widgets, delete_button))
    delete_button.grid(row=row_index, column=5, padx=5, pady=3)

    row_widgets.extend([desc_cb, hsn_entry, qty_entry, rate_entry, unit_entry])
    item_rows.append(row_widgets)

def delete_row(row_widgets, delete_button):
    if messagebox.askyesno("Delete Item", "Are you sure you want to delete this item row?"):
        for widget in row_widgets:
            widget.destroy()
        delete_button.destroy()
        item_rows.remove(row_widgets)

def generate_invoice():
    invoice_no = invoice_entry.get().strip()
    customer = customer_combobox.get().strip()
    date = datetime.now().strftime("%d-%m-%Y")

    if not invoice_no or not customer:
        messagebox.showerror("Error", "Invoice No. and Customer are required.")
        return

    items = []
    for row in item_rows:
        try:
            desc = row[0].get()
            hsn = row[1].get()
            qty = float(row[2].get())
            rate = float(row[3].get())
            unit = row[4].get()
            items.append({
                "description": desc,
                "hsn": hsn,
                "quantity": qty,
                "rate": rate,
                "unit": unit
            })
        except Exception as e:
            messagebox.showerror("Error", f"Invalid item data: {e}")
            return

    data = {
        "invoice_no": invoice_no,
        "customer": customer,
        "date": date,
        "bill_to": bill_address_entry.get("1.0", tk.END).strip(),
        "ship_to": ship_address_entry.get("1.0", tk.END).strip(),
        "mobile": mobile_entry.get().strip(),
        "gstin": gstin_entry.get().strip(),
        "pan": pan_entry.get().strip(),
        "state": state_entry.get().strip(),
        "items": items
    }

    filepath = f"data/invoices/Invoice_{invoice_no}.json"
    save_invoice_data(data, filepath)
    pdf_path = generate_pdf_invoice(data)
    messagebox.showinfo("Success", f"Invoice saved:\n{pdf_path}")

# GUI INIT
root = tk.Tk()
root.title("Billing Software")
root.geometry("1000x700")

style = ttk.Style()
if platform.system() == "Darwin":
    style.theme_use("aqua")
else:
    style.theme_use("default")

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame, highlightthickness=0)
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Mousewheel support
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

# Layout Grid
for i in range(6): scrollable_frame.columnconfigure(i, weight=1)

# Header fields
invoice_label = tk.Label(scrollable_frame, text="Invoice No:")
invoice_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
invoice_entry = tk.Entry(scrollable_frame)
invoice_entry.grid(row=0, column=1, padx=5, pady=5)

customer_label = tk.Label(scrollable_frame, text="Customer:")
customer_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)
customer_list = [c["name"] for c in load_customers()]
customer_combobox = ttk.Combobox(scrollable_frame, values=customer_list)
customer_combobox.grid(row=0, column=3, padx=5, pady=5)
customer_combobox.bind("<<ComboboxSelected>>", on_customer_selected)

add_item_btn = tk.Button(scrollable_frame, text="Add New Item to Master", command=open_add_item_dialog)
add_item_btn.grid(row=1, column=0, columnspan=6, pady=10)

# Customer info
bill_address_label = tk.Label(scrollable_frame, text="Bill To Address")
bill_address_label.grid(row=2, column=0, columnspan=2)
bill_address_entry = tk.Text(scrollable_frame, height=3, width=40)
bill_address_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

ship_address_label = tk.Label(scrollable_frame, text="Ship To Address")
ship_address_label.grid(row=2, column=2, columnspan=2)
ship_address_entry = tk.Text(scrollable_frame, height=3, width=40)
ship_address_entry.grid(row=3, column=2, columnspan=2, padx=5, pady=5)

tk.Label(scrollable_frame, text="Mobile:").grid(row=4, column=0)
mobile_entry = tk.Entry(scrollable_frame)
mobile_entry.grid(row=4, column=1)

tk.Label(scrollable_frame, text="GSTIN:").grid(row=4, column=2)
gstin_entry = tk.Entry(scrollable_frame)
gstin_entry.grid(row=4, column=3)

tk.Label(scrollable_frame, text="PAN:").grid(row=5, column=0)
pan_entry = tk.Entry(scrollable_frame)
pan_entry.grid(row=5, column=1)

tk.Label(scrollable_frame, text="State:").grid(row=5, column=2)
state_entry = tk.Entry(scrollable_frame)
state_entry.grid(row=5, column=3)

item_frame_inner = tk.Frame(scrollable_frame)
item_frame_inner.grid(row=6, column=0, columnspan=6, pady=10)

headers = ["Description", "HSN", "Qty", "Rate", "Unit"]
for i, header in enumerate(headers):
    label = tk.Label(item_frame_inner, text=header)
    label.grid(row=0, column=i, padx=5, pady=5)

item_rows = []
add_item_row()

# Controls
control_frame = tk.Frame(scrollable_frame)
control_frame.grid(row=999, column=0, columnspan=6, pady=10)

add_button = tk.Button(control_frame, text="+ Add Item", command=add_item_row)
add_button.pack(side="left", padx=10)

generate_button = tk.Button(control_frame, text="Generate Invoice", command=generate_invoice)
generate_button.pack(side="left", padx=10)

search_button = tk.Button(control_frame, text="Search Invoices")
search_button.pack(side="left", padx=10)

root.mainloop()

