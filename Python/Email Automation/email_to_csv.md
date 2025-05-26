# Step-by-Step Explanation of `email_to_csv.py`

## 1. Importing Required Libraries

```python
import re
from email import policy
from email.parser import BytesParser
import openpyxl
```

- `re`: Used for regular expression operations to extract rules from the email body.
- `email.policy` and `email.parser.BytesParser`: Used to parse the `.eml` email file and extract its content.
- `openpyxl`: Used to create and write data to Excel (`.xlsx`) files.

---

## 2. Defining File Paths

```python
EML_FILE_PATH = 'input.eml'      # Path to your .eml file
EXCEL_FILE_PATH = 'output.xlsx'  # Output Excel file
```

- `EML_FILE_PATH`: The path to the input `.eml` file containing the email.
- `EXCEL_FILE_PATH`: The path where the output Excel file will be saved.

---

## 3. Extracting the Email Body

```python
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
```

- Opens the `.eml` file in binary mode.
- Parses the email using `BytesParser`.
- If the email is multipart, it searches for a `text/plain` part first, then falls back to `text/html` if needed.
- Returns the content of the found part as a string.

---

### What is a Multipart Email?

Emails can contain multiple parts, such as plain text, HTML, and attachments. These are called **multipart emails**.

- A multipart email is structured like a container that holds several different representations of the message content.
- For example, an email might include both a `text/plain` part (for simple email clients) and a `text/html` part (for clients that support rich formatting).
- The script checks if the email is multipart using `msg.is_multipart()`. If so, it walks through each part to find and extract the plain text or HTML content.

---

## 4. Extracting Rules from the Email Body

```python
def extract_rules(text):
    """Extract rules and their values from the email body."""
    pattern = r'(Rules where .*?=)\[(.*?)\]'
    matches = re.findall(pattern, text, re.DOTALL)
    extracted = []
    for rule_desc, values in matches:
        rule_desc = rule_desc.strip().rstrip('=').strip()
        value_list = [v.strip().strip('"').strip("'") for v in values.split(',')]
        extracted.append([rule_desc] + value_list)
    return extracted
```

- Uses a regular expression to find all rule blocks in the format:  
  `Rules where ... =["value1","value2",...]`
- For each match:
  - Cleans up the rule description.
  - Splits the values by comma and removes extra quotes and whitespace.
  - Appends the rule description and its values as a list to the extracted data.

---

### Explanation of the Regex for Rule Extraction

The script uses the following regular expression to extract rules from the email body:

```python
pattern = r'(Rules where .*?=)\[(.*?)\]'
```

- `Rules where .*?=`:
  - Matches any text that starts with "Rules where", followed by any characters (non-greedy), and ending with an equals sign (`=`).
  - The `.*?` is a non-greedy match for any character (as few as possible).
- `\[(.*?)\]`:
  - Matches an opening square bracket `[`, then captures everything inside the brackets (again, non-greedy), and ends with a closing bracket `]`.
- The parentheses `()` create capture groups, so each match returns:
  1. The rule description (e.g., `Rules where Source, Destination address and Service is any =`)
  2. The values inside the brackets (e.g., `"TEST RULE 1 - VP3","Service Test"`)

This allows the script to extract both the rule description and the associated values for each rule block in the email body.

---

## 5. Saving the Extracted Data to Excel

```python
def save_to_excel(data, file_path):
    """Save extracted data to an Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Rule Description', 'Values'])
    for row in data:
        ws.append([row[0], ', '.join(row[1:])])
    wb.save(file_path)
```

- Creates a new Excel workbook and selects the active worksheet.
- Adds a header row: `Rule Description` and `Values`.
- For each extracted rule, writes the rule description and a comma-separated string of its values to the worksheet.
- Saves the workbook to the specified file path.

---

## 6. Main Function

```python
def main():
    body = extract_email_body(EML_FILE_PATH)
    rules = extract_rules(body)
    if rules:
        save_to_excel(rules, EXCEL_FILE_PATH)
        print(f"Extracted {len(rules)} rules. Data saved to {EXCEL_FILE_PATH}")
    else:
        print("No rules found in the email.")
```

- Extracts the email body from the `.eml` file.
- Extracts rules from the email body.
- If rules are found, saves them to the Excel file and prints a success message.
- If no rules are found, prints a message indicating so.

---

## 7. Script Entry Point

```python
if __name__ == "__main__":
    main()
```

- Ensures that the `main()` function runs only if the script is executed directly (not imported as a module).

---

## Summary

This script automates the process of:

1. Reading an email from a `.eml` file.
2. Extracting specific rules and their values using regular expressions.
3. Saving the extracted data into an Excel file for easy review and further processing.
