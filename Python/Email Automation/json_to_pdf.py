import json
import xlsxwriter
import re
import sys


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

    def output(self):
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
        return pdf

    def _escape(self, txt):
        return txt.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


try:
    # Read input from stdin
    raw_input = sys.stdin.read().strip()

    # Try to extract JSON array or object using regex
    array_pattern = r'="(\[.*?\])"'
    object_pattern = r'Input="({.*})"'

    json_str = None

    array_matches = re.findall(array_pattern, raw_input)
    object_match = re.search(object_pattern, raw_input)

    pdf = MinimalPDF("output.pdf")

    if array_matches and len(array_matches) > 1:
        # Process both arrays (value and regex)
        arrays = []
        for match in array_matches:
            arr = json.loads(bytes(match, "utf-8").decode("unicode_escape"))
            arrays.append(arr)

        # Add header and rows to PDF
        pdf.add_header("Keys and Values")
        columns = [(pdf.margin, pdf.get_usable_width() // 2),
                   (pdf.margin + pdf.get_usable_width() // 2, pdf.get_usable_width() // 2)]
        pdf.draw_separator(columns)

        max_len = max(len(arrays[0]), len(arrays[1]))
        for row in range(max_len):
            row_data = [
                arrays[0][row] if row < len(arrays[0]) else "",
                arrays[1][row] if row < len(arrays[1]) else ""
            ]
            pdf.draw_row(row_data, columns)

        bin_pdf = pdf.output()
        with open("output.pdf", "wb") as f:
            f.write(bin_pdf)
        print("PDF file 'output.pdf' has been created successfully.")
    elif array_matches:
        # Only one array found, process as before
        json_str = array_matches[0]
        json_str = bytes(json_str, "utf-8").decode("unicode_escape")
        data = json.loads(json_str)

        # Add header and rows to PDF
        pdf.add_header("Values")
        columns = [(pdf.margin, pdf.get_usable_width())]
        pdf.draw_separator(columns)

        for rule in data:
            pdf.cell(0, 20, str(rule))

        bin_pdf = pdf.output()
        with open("output.pdf", "wb") as f:
            f.write(bin_pdf)
        print("PDF file 'output.pdf' has been created successfully.")
    elif object_match:
        json_str = object_match.group(1)
        json_str = bytes(json_str, "utf-8").decode("unicode_escape")
        data = json.loads(json_str)
        if isinstance(data, dict) and "Commands" in data:
            commands = data["Commands"]

            # Add header and rows to PDF
            pdf.add_header("Commands")
            headers = list(commands[0].keys())
            col_width = pdf.get_usable_width() // len(headers)
            columns = [(pdf.margin + i * col_width, col_width)
                       for i in range(len(headers))]
            pdf.draw_separator(columns)

            for cmd in commands:
                row_data = [str(cmd.get(header, "")) for header in headers]
                pdf.draw_row(row_data, columns)

            bin_pdf = pdf.output()
            with open("output.pdf", "wb") as f:
                f.write(bin_pdf)
            print("PDF file 'output.pdf' has been created successfully.")
        else:
            print("Unsupported JSON structure.")
    else:
        fallback_match = re.search(r'(\{.*\}|\[.*\])', raw_input)
        if fallback_match:
            json_str = fallback_match.group(1)
            json_str = bytes(json_str, "utf-8").decode("unicode_escape")
            data = json.loads(json_str)
            if isinstance(data, list):
                # Add header and rows to PDF
                pdf.add_header("Values")
                columns = [(pdf.margin, pdf.get_usable_width())]
                pdf.draw_separator(columns)

                for rule in data:
                    pdf.cell(0, 20, str(rule))

                bin_pdf = pdf.output()
                with open("output.pdf", "wb") as f:
                    f.write(bin_pdf)
                print("PDF file 'output.pdf' has been created successfully.")
            else:
                print("Unsupported JSON structure.")
        else:
            print("No valid JSON array or object found in the input string")
except Exception as e:
    print(f"An error occurred: {e}")
