import json
from num2words import num2words

def save_invoice_data(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def amount_to_words(amount):
    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))
    words = num2words(rupees, lang='en_IN').title() + " Rupees"
    if paise > 0:
        words += f" and {num2words(paise).title()} Paise"
    return words + " Only"
