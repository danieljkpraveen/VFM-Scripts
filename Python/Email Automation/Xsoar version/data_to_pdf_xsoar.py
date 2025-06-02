import re
from datetime import datetime


######## Custom utility Class to create PDF files ########
class MinimalPDF:
    def __init__(self, filename, page_width=595, page_height=842, margin=50):
        self.filename = filename
        self.page_width = page_width
        self.page_height = page_height
        self.margin = margin
        self.objects = []
        self.pages = []
        self.current_content = ""
        self.y = page_height - margin
        self.font_size = 12
        self.leading = 16  # Line height
        self.char_width = 7  # Approximate width for Helvetica 12pt

    def set_margin(self, margin):
        """
        Sets the page margin dynamically.
        :param margin: The new margin value.
        """
        self.margin = margin
        # Reset the vertical position based on the new margin
        self.y = self.page_height - margin

    def get_usable_width(self):
        """
        Calculates the usable width of the page based on the margins.
        :return: Usable width of the page.
        """
        return self.page_width - 2 * self.margin

    def add_page(self):
        if self.current_content:
            self.pages.append(self.current_content)
            self.current_content = ""
            self.y = self.page_height - self.margin

    def set_font(self, size):
        self.font_size = size
        self.leading = int(size * 1.3)
        # Approximate char width for Helvetica (in points)
        self.char_width = int(size * 0.6)

    def text(self, x, y, txt):
        self.current_content += f"BT /F1 {self.font_size} Tf {x} {y} Td ({self._escape(txt)}) Tj ET\n"

    def wrap_text(self, txt, max_width):
        # Estimate max chars per line
        max_chars = max(int(max_width // self.char_width), 1)
        words = txt.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                if current:
                    lines.append(current)
                current = word
            else:
                if current:
                    current += " " + word
                else:
                    current = word
        if current:
            lines.append(current)
        return lines

    def draw_separator(self, columns, divider=" | "):
        """
        Draws a separator line dynamically based on the number of columns.
        :param columns: List of tuples [(col_x, col_width), ...] defining column positions and widths.
        :param divider: The divider string between columns.
        """
        for i, (col_x, col_width) in enumerate(columns):
            # Calculate separator length for the current column
            sep_len = col_width // self.char_width
            self.text(col_x, self.y, "_" * sep_len)

            # Add divider separator if not the last column
            if i < len(columns) - 1:
                next_col_x = columns[i + 1][0]
                divider_len = (next_col_x - (col_x + col_width)
                               ) // self.char_width
                self.text(col_x + col_width, self.y, "_" * divider_len)

        # Move to the next line
        self.y -= self.leading
        if self.y < self.margin:
            self.add_page()

    def draw_row(self, row_data, columns, divider=" | "):
        """
        Draws a row dynamically based on the number of columns.
        :param row_data: List of strings representing the data for each column.
        :param columns: List of tuples [(col_x, col_width), ...] defining column positions and widths.
        :param divider: The divider string between columns.
        """
        # Wrap text for each column
        wrapped_columns = [
            self.wrap_text(data, col_width) for data, (_, col_width) in zip(row_data, columns)
        ]
        max_lines = max(len(lines) for lines in wrapped_columns)

        for i in range(max_lines):
            for j, (col_x, col_width) in enumerate(columns):
                text = wrapped_columns[j][i] if i < len(
                    wrapped_columns[j]) else ""
                self.text(col_x, self.y, text)

                # Add divider if not the last column
                if j < len(columns) - 1:
                    self.text(col_x + col_width, self.y, divider)

            self.y -= self.leading
            if self.y < self.margin:
                self.add_page()

    def cell(self, w, h, txt):
        self.text(self.margin, self.y, txt)
        self.y -= self.leading
        if self.y < self.margin:
            self.add_page()

    def add_header(self, header_text):
        """
        Adds a header with a separator line below it.
        :param header_text: The text for the header.
        """
        old_font_size = self.font_size
        self.set_font(16)  # Set font size for header
        self.cell(0, 20, header_text)  # Add header text
        self.set_font(10)  # Reset font size for separator
        separator = "_" * (self.get_usable_width() // self.char_width)
        self.cell(0, 20, separator)  # Add separator line
        self.y -= self.leading  # Move to the next line
        self.set_font(old_font_size)  # Restore original font size
        if self.y < self.margin:
            self.add_page()

    def output(self, filename):
        if self.current_content:
            self.pages.append(self.current_content)
        # PDF header
        pdf = b"%PDF-1.4\n"
        xref = []
        obj_count = 1

        # Font object
        font_obj = obj_count
        font = f"{font_obj} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        pdf += font.encode()
        xref.append(len(pdf))
        obj_count += 1

        # Page content objects
        content_objs = []
        for content in self.pages:
            content_obj = obj_count
            stream = f"{content_obj} 0 obj\n<< /Length {len(content.encode())} >>\nstream\n{content}endstream\nendobj\n"
            pdf += stream.encode()
            xref.append(len(pdf))
            content_objs.append(content_obj)
            obj_count += 1

        # Page objects
        page_objs = []
        for idx, content_obj in enumerate(content_objs):
            page_obj = obj_count
            page = (f"{page_obj} 0 obj\n"
                    f"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 {self.page_width} {self.page_height}] "
                    f"/Contents {content_obj} 0 R /Resources << /Font << /F1 {font_obj} 0 R >> >> >>\n"
                    f"endobj\n")
            pdf += page.encode()
            xref.append(len(pdf))
            page_objs.append(page_obj)
            obj_count += 1

        # Pages root object
        pages_obj = obj_count
        kids = " ".join([f"{p} 0 R" for p in page_objs])
        pages = (f"{pages_obj} 0 obj\n"
                 f"<< /Type /Pages /Kids [{kids}] /Count {len(page_objs)} >>\n"
                 f"endobj\n")
        pdf += pages.encode()
        xref.append(len(pdf))
        obj_count += 1

        # Catalog object
        catalog_obj = obj_count
        catalog = (f"{catalog_obj} 0 obj\n"
                   f"<< /Type /Catalog /Pages {pages_obj} 0 R >>\n"
                   f"endobj\n")
        pdf += catalog.encode()
        xref.append(len(pdf))
        obj_count += 1

        # Xref table
        xref_start = len(pdf)
        pdf += b"xref\n0 %d\n0000000000 65535 f \n" % obj_count
        for offset in xref:
            pdf += b"%010d 00000 n \n" % offset

        # Trailer
        pdf += (f"trailer\n<< /Size {obj_count} /Root {catalog_obj} 0 R >>\nstartxref\n{xref_start}\n%%EOF\n").encode()

        # with open(self.filename, "wb") as f:
        #     f.write(pdf)

        file_entry = fileResult(filename, pdf)
        demisto.results(file_entry)

        # Put EntryID and name in context for playbook/automation chaining
        return_results(CommandResults(
            outputs_prefix="ExtractedRulesExcel",
            outputs={
                "EntryID": file_entry.get("FileID"),
                "Name": filename
            }
        ))

    def _escape(self, txt):
        return txt.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


####### Script functionality starts here ########
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

    # Pattern for quoted or unquoted task and value
    pattern_value = r'(?:"([^"]+)"|(\bRules[^\s=:-]+.*?))\s+value\s*=\s*(?:"|\')\[(.*?)\](?:"|\')'
    # Pattern for unquoted list after = or -
    pattern_list = r'(Rules.*?)(?:=|-)\s*\[(.*?)\]'
    # Pattern for single value after dash or period
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


def create_text_pdf(data, filename):
    pdf = MinimalPDF(filename)
    pdf.set_margin(30)  # Example: Set a custom margin
    pdf.set_font(9)
    pdf.add_header("Keys and Values")  # Use the new header method

    # Define columns dynamically
    columns = [
        (pdf.margin, 200),  # Column 1: X position = margin, Width = 200
        (pdf.margin + 210, 200),  # Column 2: X position = margin + 210, Width = 200
    ]
    divider = " | "

    # Rows
    for row in data:
        pdf.draw_row(row, columns, divider=divider)
        pdf.draw_separator(columns, divider=divider)

    pdf.output(filename)


def main():
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

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"rules_{timestamp}.pdf"

    pdf_data = create_text_pdf(rules, filename)

    file_entry = fileResult(filename, pdf_data)
    demisto.results(file_entry)

    # Put EntryID and name in context for playbook/automation chaining
    return_results(CommandResults(
        outputs_prefix="ExtractedRulespdf",
        outputs={
            "EntryID": file_entry.get("FileID"),
            "Name": filename
        }
    ))


if __name__ == "__main__":
    main()
