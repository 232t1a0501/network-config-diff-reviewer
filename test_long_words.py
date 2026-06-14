from fpdf import FPDF

# Create a PDF object
pdf = FPDF()
pdf.add_page()
pdf.set_font("Courier", size=10)

# A word with 100 characters and no spaces
long_word = "A" * 100

try:
    print("Trying to render a 100-character word...")
    pdf.multi_cell(0, 5, long_word, new_x="LMARGIN", new_y="NEXT")
    print("Success rendering 100 chars!")
except Exception as e:
    print("FAILED rendering 100 chars:", e)

# A word with 1000 characters and no spaces
very_long_word = "A" * 1000

try:
    print("Trying to render a 1000-character word...")
    pdf.multi_cell(0, 5, very_long_word, new_x="LMARGIN", new_y="NEXT")
    print("Success rendering 1000 chars!")
except Exception as e:
    print("FAILED rendering 1000 chars:", e)
