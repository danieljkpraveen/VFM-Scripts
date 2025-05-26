import re
from email import policy
from email.parser import BytesParser
import openpyxl

EML_FILE_PATH = 'input.eml'      # Path to your .eml file
EXCEL_FILE_PATH = 'output.xlsx'  # Output Excel file


def extract_email_body(eml_path):
    """Extracts the plain text body from a .eml file."""
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    # Prefer plain text, fallback to HTML if needed
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_content()
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                return part.get_content()
    else:
        return msg.get_content()
    return ""


def extract_rules(text):
    """Extract rules and their values from the email body."""
    pattern = r'(Rules where .*?=)\[(.*?)\]'
    matches = re.findall(pattern, text, re.DOTALL)
    extracted = []
    for rule_desc, values in matches:
        rule_desc = rule_desc.strip().rstrip('=').strip()
        value_list = [v.strip().strip('"').strip("'")
                      for v in values.split(',')]
        extracted.append([rule_desc] + value_list)
    return extracted


def save_to_excel(data, file_path):
    """Save extracted data to an Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Rule Description', 'Values'])
    for row in data:
        ws.append([row[0], ', '.join(row[1:])])
    wb.save(file_path)


def main():
    body = extract_email_body(EML_FILE_PATH)
    rules = extract_rules(body)
    if rules:
        save_to_excel(rules, EXCEL_FILE_PATH)
        print(f"Extracted {len(rules)} rules. Data saved to {EXCEL_FILE_PATH}")
    else:
        print("No rules found in the email.")


if __name__ == "__main__":
    main()
