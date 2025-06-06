import xlsxwriter
import io
import re


def extract_rules(text):
    """
    Extract rules and their values from the input.
    Handles:
      - "Rules ..." value="[\"...\",\"...\"]"
      - Rules ... value=["...", "..."]
      - Rules ... =["...", "..."]
      - Rules ... - ["...", "..."]
      - Rules ... - ... (plain text)
      - Rules ... . ... (plain text)
    """
    extracted = []

    pattern_value = r'(?:"([^"]+)"|(\bRules[^\s=:-]+.*?))\s+value\s*=\s*(?:"|\')\[(.*?)\](?:"|\')'
    pattern_list = r'(Rules.*?)(?:=|-)\s*\[(.*?)\]'
    pattern_single = r'(Rules.*?)(?:-|\.)(?!\s*\[)(.*?)(?=(?:Rules|$))'

    # First, extract all rules with quoted or unquoted value=
    for match in re.finditer(pattern_value, text, re.DOTALL):
        rule_desc = match.group(1) or match.group(2)
        values = match.group(3).replace('\\', '')
        result = ', '.join([v.strip().strip('"').strip("'")
                           for v in values.split(',')])
        extracted.append([rule_desc.strip(), result])

    # Remove already matched parts to avoid duplicates
    text = re.sub(pattern_value, '', text, flags=re.DOTALL)

    # Then, extract all rules with lists (excluding value=)
    for match in re.finditer(pattern_list, text, re.DOTALL):
        rule_desc = match.group(1).strip().rstrip('= -').strip()
        values = match.group(2).replace('\\', '')
        result = ', '.join([v.strip().strip('"').strip("'")
                           for v in values.split(',')])
        extracted.append([rule_desc, result])

    # Remove already matched parts to avoid duplicates
    text_cleaned = re.sub(pattern_list, '', text, flags=re.DOTALL)

    # Now extract single-value rules (not followed by [ ... ])
    for match in re.finditer(pattern_single, text_cleaned, re.DOTALL):
        rule_desc = match.group(1).strip().rstrip('= -').strip()
        value = match.group(2).strip().strip('.').strip()
        if value:
            extracted.append([rule_desc, value])

    return extracted


def create_text_excel(data, filename):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold_center = workbook.add_format(
        {'bold': True, 'align': 'center', 'valign': 'vcenter'})

    headers = ["Tasks", "Results"]
    all_rows = [headers] + data

    col_widths = [0, 0]
    for row in all_rows:
        for col, cell in enumerate(row):
            cell_len = len(str(cell))
            if cell_len > col_widths[col]:
                col_widths[col] = cell_len

    col_widths = [w + 2 for w in col_widths]
    worksheet.set_column(0, 0, col_widths[0])
    worksheet.set_column(1, 1, col_widths[1])

    worksheet.write(0, 0, headers[0], bold_center)
    worksheet.write(0, 1, headers[1], bold_center)

    for i, row in enumerate(data, start=1):
        worksheet.write_row(i, 0, row)

    workbook.close()
    output.seek(0)
    return output.read()


def main():
    # Defensive argument extraction and logging for XSOAR quirks
    args = demisto.args()
    demisto.info(f'Args received: {args}')
    input_text = args.get("input_text", "")
    if not input_text:
        input_text = next(iter(args.values()), "")
    if isinstance(input_text, (dict, list)):
        input_text = str(input_text)
    input_text = input_text.replace('\r\n', '\n')
    demisto.info(f'Input text: {input_text}')

    rules = extract_rules(input_text)
    filename = "rules.xlsx"
    excel_data = create_text_excel(rules, filename)

    # Attach file to War Room for users
    file_entry = fileResult(filename, excel_data)
    demisto.results(file_entry)

    # Put EntryID and name in context for playbook/automation chaining
    return_results(CommandResults(
        outputs_prefix="ExtractedRulesExcel",
        outputs={
            "EntryID": file_entry.get("FileID"),
            "Name": filename
        }
    ))


if __name__ in ("__builtin__", "builtins", "__main__"):
    main()
