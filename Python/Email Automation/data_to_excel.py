import re
import sys
import pandas as pd
from bs4 import BeautifulSoup
import os
import openpyxl  # Add this import at the top
import datetime


def read_stdin():
    print("Paste your plain text or HTML input. Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) then Enter to finish:")
    return sys.stdin.read()


def is_html(text):
    return bool(BeautifulSoup(text, "html.parser").find())


def extract_rules(text):
    """Extract rules and their values from the input."""
    pattern = r'(Rules where .*?=)\[(.*?)\]'
    matches = re.findall(pattern, text, re.DOTALL)
    extracted = []
    for rule_desc, values in matches:
        task = rule_desc.strip().rstrip('=').strip()
        result = ', '.join([v.strip().strip('"').strip("'")
                           for v in values.split(',')])
        extracted.append([task, result])
    return extracted


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")


def save_to_excel(data, file_path):
    df = pd.DataFrame(data, columns=["Tasks", "Results"])
    df.to_excel(file_path, index=False)

    # Auto-adjust column widths using openpyxl
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    for column_cells in ws.columns:
        length = max(len(str(cell.value))
                     if cell.value else 0 for cell in column_cells)
        # Add padding
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2
    wb.save(file_path)
    print(f"Data saved to {file_path}")


def main():
    input_text = read_stdin()
    if is_html(input_text):
        print("Detected HTML input.")
        text = html_to_text(input_text)
    else:
        print("Detected plain text input.")
        text = input_text
    rules = extract_rules(text)
    if rules:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"output_{now}.xlsx"
        save_to_excel(rules, excel_path)
        print(f"Extracted {len(rules)} rules. Data saved to {excel_path}")
    else:
        print("No rules found in the input.")


if __name__ == "__main__":
    main()
