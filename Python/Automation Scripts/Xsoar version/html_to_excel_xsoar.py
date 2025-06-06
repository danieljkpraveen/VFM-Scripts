import os
import re
import sys
# from bs4 import BeautifulSoup
import io
import xlsxwriter


# def is_html(text):
#     return bool(BeautifulSoup(text, "html.parser").find())


def extract_rules(text):
    """
    Extract rules and their values from the input.
    Handles:
      - Rules ... =["...", "..."]
      - Rules ... - ["...", "..."]
      - Rules ... - ... (plain text)
      - Rules ... . ... (plain text)
    """
    # Pattern for rules with a list of values in brackets
    pattern_list = r'(Rules.*?)(?:=|-)\s*\[(.*?)\]'
    # Pattern for rules with a single value after dash or period
    pattern_single = r'(Rules.*?)(?:-|\.)(?!\s*\[)(.*?)(?=(?:Rules|$))'

    extracted = []

    # First, extract all rules with lists
    for match in re.finditer(pattern_list, text, re.DOTALL):
        rule_desc = match.group(1).strip().rstrip('= -').strip()
        values = match.group(2)
        result = ', '.join([v.strip().strip('"').strip("'")
                           for v in values.split(',')])
        extracted.append([rule_desc, result])

    # Remove already matched parts to avoid duplicates
    text_cleaned = re.sub(pattern_list, '', text, flags=re.DOTALL)

    # Now extract single-value rules (not followed by [ ... ])
    for match in re.finditer(pattern_single, text_cleaned, re.DOTALL):
        rule_desc = match.group(1).strip().rstrip('= -').strip()
        value = match.group(2).strip().strip('.').strip()
        if value:  # Only add if value is not empty
            extracted.append([rule_desc, value])

    return extracted


# def extract_interface_table_from_html(html):
#     """Extracts interface table from Cisco CLI HTML output."""
#     soup = BeautifulSoup(html, "html.parser")
#     cli_div = soup.find("div", class_="cli-output")
#     if not cli_div:
#         return [], []

#     lines = cli_div.get_text(separator="\n").splitlines()
#     table_start = None
#     for idx, line in enumerate(lines):
#         if line.strip().startswith("Interface"):
#             table_start = idx
#             break
#     if table_start is None:
#         return [], []

#     headers = ["Interface", "IP-Address", "Method", "Status", "Protocol"]
#     data = []
#     for line in lines[table_start+1:]:
#         if not line.strip():
#             continue
#         parts = [p for p in line.replace('\xa0', ' ').split(' ') if p]
#         if len(parts) < 6:
#             continue
#         interface = parts[0]
#         ip_addr = parts[1]
#         method = parts[3]
#         status = parts[4]
#         protocol = parts[5]
#         data.append([interface, ip_addr, method, status, protocol])
#     return headers, data


def create_text_excel(data, filename):
    """Excel generation for plain text rules with auto-fit columns."""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Centered bold header format
    bold_center = workbook.add_format(
        {'bold': True, 'align': 'center', 'valign': 'vcenter'})

    # Prepare headers and combine with data for width calculation
    headers = ["Tasks", "Results"]
    all_rows = [headers] + data

    # Calculate max width for each column
    col_widths = [0, 0]
    for row in all_rows:
        for col, cell in enumerate(row):
            cell_len = len(str(cell))
            if cell_len > col_widths[col]:
                col_widths[col] = cell_len

    # Add some padding for readability
    col_widths = [w + 2 for w in col_widths]

    # Set column widths
    worksheet.set_column(0, 0, col_widths[0])
    worksheet.set_column(1, 1, col_widths[1])

    # Write headers
    worksheet.write(0, 0, headers[0], bold_center)
    worksheet.write(0, 1, headers[1], bold_center)

    # Write data
    for i, row in enumerate(data, start=1):
        worksheet.write_row(i, 0, row)

    workbook.close()
    output.seek(0)
    return fileResult(filename, output.read())


# def create_html_excel(data, headers, filename):
#     """Excel generation for HTML-extracted interface tables with row coloring and auto-fit columns."""
#     output = io.BytesIO()
#     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#     worksheet = workbook.add_worksheet()

#     bold = workbook.add_format({'bold': True})
#     green_fill = workbook.add_format(
#         {'bg_color': '#C6EFCE', 'font_color': '#000000'})
#     red_fill = workbook.add_format(
#         {'bg_color': '#FFC7CE', 'font_color': '#000000'})
#     normal = workbook.add_format({'font_color': '#000000'})

#     # Combine headers and data for width calculation
#     all_rows = [headers] + data

#     # Calculate max width for each column
#     col_widths = [0] * len(headers)
#     for row in all_rows:
#         for col, cell in enumerate(row):
#             cell_len = len(str(cell))
#             if cell_len > col_widths[col]:
#                 col_widths[col] = cell_len

#     # Add some padding for readability
#     col_widths = [w + 2 for w in col_widths]

#     # Set column widths
#     for col, width in enumerate(col_widths):
#         worksheet.set_column(col, col, width)

#     # Write headers
#     for col, header in enumerate(headers):
#         worksheet.write(0, col, header, bold)

#     # Find the index of the "Status" column
#     try:
#         status_idx = headers.index('Status')
#     except ValueError:
#         status_idx = -1

#     # Write data with row-based conditional formatting
#     for row_num, row_data in enumerate(data, start=1):
#         row_format = normal
#         if status_idx != -1:
#             status_value = str(row_data[status_idx]).lower()
#             if status_value == 'up':
#                 row_format = green_fill
#             elif status_value == 'down':
#                 row_format = red_fill
#         for col, value in enumerate(row_data):
#             worksheet.write(row_num, col, value, row_format)

#     workbook.close()
#     output.seek(0)
#     return fileResult(filename, output.read())


def get_downloads_folder():
    """Return the user's Downloads folder path in a cross-platform way."""
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


def main():
    try:
        input_text = demisto.args().get('input')
        if not input_text:
            return_error("No input provided.")

        # downloads_folder = get_downloads_folder()
        # os.makedirs(downloads_folder, exist_ok=True)

        # if is_html(input_text):
        #     headers, data = extract_interface_table_from_html(input_text)
        #     if data:
        #         headers = ["Interface", "IP-Address",
        #                    "Method", "Status", "Protocol"]
        #         filename = os.path.join(downloads_folder, "interfaces.xlsx")
        #         return_results(create_html_excel(data, headers, filename))
        #     else:
        #         return_error("No interface table found in HTML.")
        # else:
        rules = extract_rules(input_text)
        if rules:
            filename = "rules.xlsx"
            return_results(create_text_excel(rules, filename))
        else:
            return_error("No rules found in the input.")
    except Exception as e:
        return_error(f"Script failed: {str(e)}")


if __name__ == "__main__":
    main()
