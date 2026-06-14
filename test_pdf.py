from fpdf import FPDF
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.utils import markdown_to_pdf_bytes

# Read the actual failed_report.md
report_path = "outputs/failed_report.md"
with open(report_path, "r", encoding="utf-8") as f:
    markdown_text = f.read()

def test_markdown_to_pdf_bytes_debug(markdown_text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=10)

    for i, raw_line in enumerate(markdown_text.split("\n")):
        line = raw_line.replace("\t", "    ")
        line = line.encode("latin-1", errors="replace").decode("latin-1")
        if not line.strip():
            pdf.ln(4)
            continue
        
        # Simple heading emphasis
        try:
            if line.startswith("# "):
                pdf.set_font("Courier", "B", 14)
                pdf.multi_cell(0, 8, line.replace("# ", ""), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Courier", size=10)
            elif line.startswith("## "):
                pdf.set_font("Courier", "B", 12)
                pdf.multi_cell(0, 7, line.replace("## ", ""), new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Courier", size=10)
            else:
                pdf.multi_cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        except Exception as e:
            print(f"FAILED ON LINE {i}: {repr(line)}")
            print(f"pdf.x = {pdf.get_x()}, pdf.y = {pdf.get_y()}")
            raise e

    return bytes(pdf.output())

try:
    print("Testing with outputs/final_report.md...")
    pdf_bytes = test_markdown_to_pdf_bytes_debug(markdown_text)
    print("Success! PDF bytes length:", len(pdf_bytes))
except Exception as e:
    import traceback
    print("Failed with exception:")
    traceback.print_exc()
