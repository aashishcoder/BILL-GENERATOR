from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from utils import amount_to_words
import os
import datetime

# Register fonts
font_path_regular = "assets/fonts/NotoSans-Regular.ttf"
font_path_bold = "assets/fonts/NotoSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("NotoSans", font_path_regular))
pdfmetrics.registerFont(TTFont("NotoSans-Bold", font_path_bold))

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

    # Header
    c.setFont("NotoSans-Bold", 14)
    c.setFillColorRGB(*green)
    c.drawString(30, height - 40, "AONE PET RECYCLERS")

    c.setFont("NotoSans", 9)
    c.setFillColorRGB(*black)
    c.drawString(30, height - 55, "PART OF PL. NO. C-39, C-40, AND C-41, PL. NO. C-17, Unnamed Road, Panchayat Headquarter, ETMADPUR, Po iya, Agra")
    c.drawString(30, height - 67, "Mobile: 9897201594    GSTIN: 09EMMPK5033B1Z5")
    c.drawString(30, height - 79, "Email: kumarhim28@gmail.com")

    # Invoice Info
    c.setFont("NotoSans-Bold", 10)
    c.drawString(30, height - 100, f"Invoice No.: {invoice_no}")
    c.drawRightString(560, height - 100, f"Invoice Date: {date}")

    # Bill To / Ship To
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, height - 120, "BILL TO")
    c.drawString(300, height - 120, "SHIP TO")

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
        y = height - 135 - (i * 12)
        c.drawString(30, y, line)
        c.drawString(300, y, line)

    # Table Header
    table_y = height - 240
    c.setFont("NotoSans-Bold", 9)
    c.setStrokeColorRGB(*green)
    c.setLineWidth(0.7)
    c.line(30, table_y + 5, 560, table_y + 5)
    c.drawString(30, table_y, "ITEMS")
    c.drawString(230, table_y, "HSN")
    c.drawString(280, table_y, "QTY.")
    c.drawString(330, table_y, "RATE")
    c.drawString(390, table_y, "TAX")
    c.drawString(460, table_y, "AMOUNT")
    c.line(30, table_y - 2, 560, table_y - 2)

    # Table Rows
    y = table_y - 15
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

        c.drawString(30, y, desc)
        c.drawString(230, y, str(hsn))
        c.drawString(280, y, f"{qty:.1f} KGS")
        c.drawString(330, y, f"₹{rate:.1f}")
        c.drawString(390, y, f"₹{tax:,.0f}")
        c.drawString(460, y, f"₹{total:,.0f}")

        subtotal += amount
        total_tax += tax
        y -= 15

    total_amount = subtotal + total_tax

    # Totals Summary
    c.setFont("NotoSans-Bold", 9)
    y -= 10
    c.line(30, y + 5, 560, y + 5)
    c.drawString(280, y, "SUBTOTAL")
    c.drawString(390, y, f"₹{total_tax:,.0f}")
    c.drawString(460, y, f"₹{total_amount:,.0f}")
    y -= 20

    # Terms & Conditions
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, y, "TERMS AND CONDITIONS")
    c.setFont("NotoSans", 8)
    c.drawString(30, y - 12, "1. Goods once sold will not be taken back or exchanged.")
    c.drawString(30, y - 24, "2. All disputes are subject to Agra jurisdiction only.")

    # Right Side Totals
    c.setFont("NotoSans", 8)
    right_y = y
    c.drawRightString(550, right_y, "TAXABLE AMOUNT")
    c.drawRightString(580, right_y, f"₹ {subtotal:,.2f}")
    c.drawRightString(550, right_y - 12, "CGST @9%")
    c.drawRightString(580, right_y - 12, f"₹ {subtotal * 0.09:,.2f}")
    c.drawRightString(550, right_y - 24, "SGST @9%")
    c.drawRightString(580, right_y - 24, f"₹ {subtotal * 0.09:,.2f}")

    c.setFont("NotoSans-Bold", 9)
    c.drawRightString(550, right_y - 36, "TOTAL AMOUNT")
    c.drawRightString(580, right_y - 36, f"₹ {total_amount:,.2f}")

    # Amount in Words
    c.setFont("NotoSans", 8)
    c.drawString(30, y - 60, "Total Amount (in words)")
    c.setFont("NotoSans-Bold", 9)
    c.drawString(30, y - 72, amount_to_words(total_amount))

    c.save()
    return filename