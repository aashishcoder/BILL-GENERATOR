from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Image
from utils import amount_to_words
import os
import datetime
import csv
import qrcode

# Register fonts
font_path_regular = "assets/fonts/NotoSans-Regular.ttf"
font_path_bold = "assets/fonts/NotoSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("NotoSans", font_path_regular))
pdfmetrics.registerFont(TTFont("NotoSans-Bold", font_path_bold))

def generate_qr_code(data, invoice_no):
    qr_path = f"data/qrcodes/invoice_{invoice_no}.png"
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    subtotal = sum(i["rate"] * i["quantity"] for i in data["items"])
    tax = subtotal * 0.18
    total = subtotal + tax

    qr_content = (
        f"Invoice No: {invoice_no}\n"
        f"Customer: {data['customer']}\n"
        f"Tax Amount: ₹{tax:,.2f}\n"
        f"Total Amount: ₹{total:,.2f}"
    )

    qr = qrcode.make(qr_content)
    qr.save(qr_path)
    return qr_path

def export_invoice_to_csv(data, invoice_no):
    export_path = f"data/exports/invoice_{invoice_no}.csv"
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Description", "HSN", "Quantity", "Rate", "Tax", "Total"])
        for item in data["items"]:
            amount = item["rate"] * item["quantity"]
            tax = amount * 0.18
            total = amount + tax
            writer.writerow([item["description"], item["hsn"], item["quantity"], item["rate"], f"{tax:.2f}", f"{total:.2f}"])
    return export_path

def generate_pdf_invoice(data):
    invoice_no = data["invoice_no"]
    customer = data["customer"]
    items = data["items"]
    date = data.get("date") or datetime.datetime.now().strftime("%d-%m-%Y")

    filename = f"data/invoices/Invoice_{invoice_no}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Colors
    green = (0.2, 0.6, 0.2)
    black = (0, 0, 0)

    # Header Title
    c.setFont("NotoSans-Bold", 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width / 2, height - 30, "TAX INVOICE - ORIGINAL")

    # Logo and Company Name
    logo_path = "assets/logo/logo.png"
    logo_width = 40
    logo_height = 40
    logo_x = 30
    logo_y = height - 80
    if os.path.exists(logo_path):
        c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto', preserveAspectRatio=True)

    c.setFont("NotoSans-Bold", 14)
    c.setFillColorRGB(*green)
    c.drawString(logo_x + logo_width + 15, logo_y + logo_height / 2 - 5, "AONE PET RECYCLERS")

    # Address and Contact
    c.setFont("NotoSans", 9)
    c.setFillColorRGB(*black)
    address_y = logo_y - 10
    c.drawString(30, address_y, "PART OF PL. NO. C-39, C-40, AND C-41, PL. NO. C-17, UNNAMED ROAD, PANCHAYAT HEADQUARTER, ETMADPUR, POIYA, AGRA")

    # Mobile, GSTIN, Email with bold labels
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, address_y - 12, "Mobile:")
    c.setFont("NotoSans", 9)
    c.drawString(70, address_y - 12, "9897201594")

    c.setFont("NotoSans-Bold", 9)
    c.drawString(180, address_y - 12, "GSTIN:")
    c.setFont("NotoSans", 9)
    c.drawString(220, address_y - 12, "09EMMPK5033B1Z5")

    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, address_y - 24, "Email:")
    c.setFont("NotoSans", 9)
    c.drawString(70, address_y - 24, "kumarhim28@gmail.com")

    # Invoice Box - only top border thick and grey background
    box_y = address_y - 50
    box_width = 530
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(30, box_y, box_width, 20, fill=1, stroke=0)
    c.setStrokeColorRGB(*green)
    c.setLineWidth(2)
    c.line(30, box_y + 20, 30 + box_width, box_y + 20)  # Top border only

    # Text inside box
    c.setFont("NotoSans-Bold", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(35, box_y + 5, f"Invoice No.: {invoice_no}")
    c.drawRightString(550, box_y + 5, f"Invoice Date: {date}")



    # Bill To / Ship To
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, address_y - 65, "BILL TO:")
    c.drawString(300, address_y - 65, "SHIP TO:")

    bill_text = [
        "V.C. MONO FILAMENT INDUSTRIES",
        "Abanton no. 890, flat no. 1,2,3, near kiran marble, Runakta,",
        "Agra, Uttar Pradesh, Agra, 282007",
        "Mobile: 9917502040",
        "GSTIN: 09AAPFV5164M1ZA",
        "PAN Number: AAPFV5164M",
        "State: Uttar Pradesh"
    ]
    c.setFont("NotoSans", 9)
    for i, line in enumerate(bill_text):
        y = address_y - 80 - (i * 12)
        c.drawString(30, y, line)
        c.drawString(300, y, line)

    # Table Header
    table_y = address_y - 170
    c.setFont("NotoSans-Bold", 9)
    c.setStrokeColorRGB(*green)
    c.setLineWidth(0.7)
    c.rect(30, table_y - 15, 530, 15, stroke=1, fill=0)
    headers = ["ITEMS", "HSN", "QTY.", "RATE", "TAX", "AMOUNT"]
    x_positions = [32, 190, 250, 310, 370, 460]
    for i, header in enumerate(headers):
        c.drawString(x_positions[i], table_y - 12, header)

    # Table Rows
    y = table_y - 30
    subtotal = 0
    total_tax = 0
    c.setFont("NotoSans", 9)
    for item in items:
        desc = item["description"]
        hsn = item["hsn"]
        qty = item["quantity"]
        rate = item["rate"]
        amount = qty * rate
        cgst = sgst = amount * 0.09
        tax = cgst + sgst
        total = amount + tax

        row_height = 15
        c.rect(30, y, 530, row_height, stroke=1, fill=0)
        c.drawString(32, y + 3, desc[:30])
        c.drawString(190, y + 3, str(hsn))
        c.drawCentredString(270, y + 3, f"{qty:.1f}")
        c.drawRightString(340, y + 3, f"₹{rate:.1f}")
        c.drawRightString(420, y + 3, f"₹{tax:,.2f}")
        c.drawRightString(550, y + 3, f"₹{total:,.2f}")

        subtotal += amount
        total_tax += tax
        y -= row_height

    total_amount = subtotal + total_tax

    # Totals Summary
    c.setFont("NotoSans-Bold", 9)
    c.line(30, y + 10, 560, y + 10)
    c.drawString(280, y, "SUBTOTAL")
    c.drawRightString(420, y, f"₹{total_tax:,.2f}")
    c.drawRightString(550, y, f"₹{total_amount:,.2f}")
    y -= 25

    # Terms & Conditions
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, y, "TERMS AND CONDITIONS")
    c.setFont("NotoSans", 8)
    c.drawString(30, y - 12, "1. Goods once sold will not be taken back or exchanged.")
    c.drawString(30, y - 24, "2. All disputes are subject to Agra jurisdiction only.")

    # Right Side Totals with fixed label/value alignment
    c.setFont("NotoSans", 8)
    label_x = 400
    value_x = 560
    right_y = y
    c.drawString(label_x, right_y, "TAXABLE AMOUNT")
    c.drawRightString(value_x, right_y, f"₹ {subtotal:,.2f}")
    c.drawString(label_x, right_y - 12, "CGST @9%")
    c.drawRightString(value_x, right_y - 12, f"₹ {subtotal * 0.09:,.2f}")
    c.drawString(label_x, right_y - 24, "SGST @9%")
    c.drawRightString(value_x, right_y - 24, f"₹ {subtotal * 0.09:,.2f}")

    c.setFont("NotoSans-Bold", 9)
    c.drawString(label_x, right_y - 36, "TOTAL AMOUNT")
    c.drawRightString(value_x, right_y - 36, f"₹ {total_amount:,.2f}")

    # Amount in Words
    c.setFont("NotoSans", 8)
    c.drawString(30, right_y - 60, "Total Amount (in words)")
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, right_y - 72, amount_to_words(total_amount))

    # QR Code at the bottom
    qr_path = generate_qr_code(data, invoice_no)
    if os.path.exists(qr_path):
        c.drawImage(qr_path, 500, right_y - 160, width=60, height=60)

    c.save()
    export_invoice_to_csv(data, invoice_no)
    return filename
