import re
import sys
import datetime
from fpdf import FPDF
from bs4 import BeautifulSoup


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


def split_text_to_lines(pdf, text, col_width):
    # Splits text into lines that fit the column width
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if pdf.get_string_width(test_line) > col_width:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    return lines


def save_to_pdf_table(data, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    col_widths = [80, 100]
    row_height = 10

    # Table headers
    pdf.cell(col_widths[0], row_height, "Tasks", border=1, align="C")
    pdf.cell(col_widths[1], row_height, "Results", border=1, align="C")
    pdf.ln()

    for row in data:
        lines_0 = split_text_to_lines(pdf, row[0], col_widths[0])
        lines_1 = split_text_to_lines(pdf, row[1], col_widths[1])
        n_lines = max(len(lines_0), len(lines_1))

        # Pad shorter column
        lines_0 += [""] * (n_lines - len(lines_0))
        lines_1 += [""] * (n_lines - len(lines_1))

        for i in range(n_lines):
            pdf.cell(col_widths[0], row_height, lines_0[i], border=1)
            pdf.cell(col_widths[1], row_height, lines_1[i], border=1)
            pdf.ln()

    pdf.output(file_path)


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
        filename = f"output_{now}.pdf"
        save_to_pdf_table(rules, filename)
        print(f"Extracted {len(rules)} rules. Data saved to {filename}")
    else:
        print("No rules found in the input.")


if __name__ == "__main__":
    main()
