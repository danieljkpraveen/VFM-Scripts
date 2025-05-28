# Detailed Explanation of `data_to_excel.py`

This script is designed to process either plain text or HTML input (such as Cisco CLI output), extract structured data, and export it to an Excel file with formatting. Below is a step-by-step explanation of the code:

---

## 1. **Imports**

```python
import re
import sys
import pandas as pd
from bs4 import BeautifulSoup
import openpyxl
import datetime
```

- **re**: For regular expressions (pattern matching).
- **sys**: For reading standard input.
- **pandas**: For handling tabular data and exporting to Excel.
- **BeautifulSoup**: For parsing HTML.
- **openpyxl**: For formatting Excel files.
- **datetime**: For timestamping output files.

---

## 2. **Reading Input**

```python
def read_stdin():
    print("Paste your plain text or HTML input. Press Ctrl+v to paste then Ctrl+d to finish:")
    return sys.stdin.read()
```

- Prompts the user to paste input (plain text or HTML).
- Reads all input from standard input until EOF.

---

## 3. **HTML Detection**

```python
def is_html(text):
    return bool(BeautifulSoup(text, "html.parser").find())
```

- Uses BeautifulSoup to check if the input contains any HTML elements.

---

## 4. **Extracting Rules from Plain Text**

```python
def extract_rules(text):
    pattern = r'(Rules where .*?=)\[(.*?)\]'
    matches = re.findall(pattern, text, re.DOTALL)
    extracted = []
    for rule_desc, values in matches:
        task = rule_desc.strip().rstrip('=').strip()
        result = ', '.join([v.strip().strip('"').strip("'") for v in values.split(',')])
        extracted.append([task, result])
    return extracted
```

- Uses a regex to find patterns like `Rules where ... = [ ... ]`.
- Extracts the rule description and the list of values.
- Cleans up and formats the extracted data into a list of `[task, result]` pairs.

---

## 5. **HTML to Plain Text Conversion**

```python
def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")
```

- Converts HTML content to plain text, separating elements by newlines.

---

## 6. **Extracting Interface Table from Cisco CLI HTML Output**

```python
def extract_interface_table_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    cli_div = soup.find("div", class_="cli-output")
    if not cli_div:
        return [], []

    lines = cli_div.get_text(separator="\n").splitlines()
    table_start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("Interface"):
            table_start = idx
            break
    if table_start is None:
        return [], []

    headers = ["Interface", "IP-Address", "Method", "Status", "Protocol"]
    data = []
    for line in lines[table_start+1:]:
        if not line.strip():
            continue
        parts = [p for p in line.replace('\xa0', ' ').split(' ') if p]
        if len(parts) < 6:
            continue
        interface = parts[0]
        ip_addr = parts[1]
        method = parts[3]
        status = parts[4]
        protocol = parts[5]
        data.append([interface, ip_addr, method, status, protocol])
    return headers, data
```

- Parses the HTML to find a `<div>` with class `cli-output`.
- Searches for the line starting with "Interface" to locate the table header.
- Extracts subsequent lines as table rows, splitting and cleaning up the data.
- Returns headers and the extracted data.

---

## 7. **Exporting Plain Text Data to Excel**

```python
def text_data_to_excel(data, file_path):
    df = pd.DataFrame(data, columns=["Tasks", "Results"])
    df.to_excel(file_path, index=False)

    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2
    wb.save(file_path)
    print(f"Data saved to {file_path}")
```

- Converts the extracted rules to a DataFrame and saves to Excel.
- Adjusts column widths for readability.

---

## 8. **Exporting HTML Table Data to Excel with Formatting**

```python
def html_data_to_excel(data, file_path, headers):
    df = pd.DataFrame(data, columns=headers)
    df.to_excel(file_path, index=False)

    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    # Bold headers
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    # Auto-adjust column widths
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    # Highlight rows based on Status
    if "Status" in headers:
        status_col = headers.index("Status") + 1
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            status = row[status_col-1].value
            if status and str(status).lower() == "up":
                for cell in row:
                    cell.fill = openpyxl.styles.PatternFill(
                        start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            elif status and str(status).lower() == "down":
                for cell in row:
                    cell.fill = openpyxl.styles.PatternFill(
                        start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

    wb.save(file_path)
    print(f"Data saved to {file_path}")
```

- Converts the extracted interface table to a DataFrame and saves to Excel.
- Bolds the header row.
- Adjusts column widths.
- Highlights rows green if Status is "up", red if "down".

---

## 9. **Main Function**

```python
def main():
    input_text = read_stdin()
    if is_html(input_text):
        print("Detected HTML input.")
        headers, table_data = extract_interface_table_from_html(input_text)
        if table_data:
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = f"interfaces_{now}.xlsx"
            html_data_to_excel(table_data, excel_path, headers)
            print(f"Extracted {len(table_data)} interfaces. Data saved to {excel_path}")
            return
        else:
            print("No interface table found in the HTML input.")
    else:
        print("Detected plain text input.")
        text = input_text
        rules = extract_rules(text)
        if rules:
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = f"output_{now}.xlsx"
            text_data_to_excel(rules, excel_path)
            print(f"Extracted {len(rules)} rules. Data saved to {excel_path}")
        else:
            print("No rules found in the input.")
```

- Reads input from the user.
- Detects if the input is HTML or plain text.
- Extracts and exports the relevant data to an Excel file with a timestamped filename.
- Provides feedback on what was extracted and where it was saved.

---

## 10. **Script Entry Point**

```python
if __name__ == "__main__":
    main()
```

- Ensures the script runs the `main()` function when executed directly.

---

## **Summary**

- The script can process both plain text and HTML input.
- It extracts structured data (rules or interface tables) and exports it to Excel.
- The Excel output is formatted for readability and highlights important statuses.
- The script is interactive and user-friendly, suitable for automating data extraction from network device outputs or similar sources.
