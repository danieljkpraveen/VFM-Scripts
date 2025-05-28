# Step-by-Step Explanation of `data_to_pdf.py`

This script reads plain text or HTML input (typically pasted by the user), extracts specific "rules" from the text, and saves them in a formatted PDF table. Here’s a detailed breakdown of how it works:

---

## 1. **Imports**

- `re`: For regular expressions to extract rules from the text.
- `sys`: To read input from standard input (stdin).
- `datetime`: For timestamping the output PDF filename.
- `FPDF`: To create and format PDF files.
- `BeautifulSoup`: To parse and extract text from HTML input.

---

## 2. **Function: `read_stdin()`**

- Prompts the user to paste their input (plain text or HTML).
- Reads all input from stdin until EOF (`Ctrl+D`).
- Returns the input as a string.

---

## 3. **Function: `is_html(text)`**

- Uses BeautifulSoup to parse the input.
- Returns `True` if any HTML element is found, otherwise `False`.

---

## 4. **Function: `extract_rules(text)`**

- Uses a regular expression to find all patterns like:  
  `Rules where ... = [ ... ]`
- For each match:
  - Extracts the rule description (before the `=`) and the values (inside the brackets).
  - Cleans up the description and splits the values by comma.
  - Strips extra whitespace and quotes from each value.
  - Appends a `[task, result]` pair to the results list.
- Returns a list of `[task, result]` pairs.

---

## 5. **Function: `html_to_text(html)`**

- Uses BeautifulSoup to convert HTML input into plain text.
- Preserves line breaks between elements.

---

## 6. **Function: `split_text_to_lines(pdf, text, col_width)`**

- Splits a string into multiple lines so that each line fits within a specified column width in the PDF.
- Uses the PDF’s font metrics to measure string width.
- Returns a list of lines.

---

## 7. **Function: `save_to_pdf_table(data, file_path)`**

- Creates a new PDF document.
- Sets up two columns: "Tasks" and "Results".
- For each row in the data:
  - Splits both columns into lines that fit their respective widths.
  - Pads shorter columns so both have the same number of lines.
  - Writes each line pair into the PDF as a table row.
- Saves the PDF to the specified file path.

---

## 8. **Function: `main()`**

- Reads user input.
- Detects if the input is HTML or plain text.
- Converts HTML to text if needed.
- Extracts rules from the text.
- If rules are found:
  - Generates a timestamped filename.
  - Saves the rules to a PDF table.
  - Prints a success message.
- If no rules are found, prints a message.

---

## 9. **Script Entry Point**

- If the script is run directly, it calls `main()`.

---

## **Summary**

- **Input:** User pastes plain text or HTML containing "Rules where ... = [ ... ]".
- **Processing:** Extracts rules, optionally converts HTML to text, formats data.
- **Output:** Saves extracted rules as a two-column table in a PDF file.
