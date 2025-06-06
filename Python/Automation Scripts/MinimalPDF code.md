# MinimalPDF Class Explanation

The `MinimalPDF` class is a lightweight implementation for generating PDF files programmatically. Below is a detailed step-by-step explanation of its functionality:

---

### **1. Constructor (`__init__`)**

The constructor initializes the PDF object with the following parameters:

- `filename`: Name of the output PDF file.
- `page_width` and `page_height`: Dimensions of the PDF page (default is A4 size: 595x842 points).
- `margin`: Margin size around the page content.
- Other attributes:
  - `objects`: List to store PDF objects.
  - `pages`: List to store page content.
  - `current_content`: String to hold the current page's content.
  - `y`: Vertical position for text placement, starting at the top minus the margin.
  - `font_size`, `leading`, and `char_width`: Font size, line height, and approximate character width for text rendering.

---

### **2. `set_margin`**

Updates the margin dynamically and recalculates the vertical position (`y`) based on the new margin.

---

### **3. `get_usable_width`**

Calculates the usable width of the page by subtracting the margins from the total page width.

---

### **4. `add_page`**

Adds the current page's content to the `pages` list and resets the `current_content` and vertical position (`y`) for the next page.

---

### **5. `set_font`**

Sets the font size and recalculates:

- `leading`: Line height based on font size.
- `char_width`: Approximate width of a character for the Helvetica font.

---

### **6. `text`**

Adds text to the current page content using PDF syntax:

- `BT`: Begin text object.
- `/F1 {font_size} Tf`: Set font and size.
- `{x} {y} Td`: Set text position.
- `({txt}) Tj`: Render text.
- `ET`: End text object.

---

### **7. `wrap_text`**

Wraps text into multiple lines based on the maximum width:

- Splits the text into words.
- Groups words into lines that fit within the specified width.
- Returns a list of wrapped lines.

---

### **8. `draw_separator`**

Draws a separator line across columns:

- Iterates through column positions and widths.
- Calculates the separator length based on column width and character width.
- Adds a divider between columns if applicable.
- Moves to the next line and adds a new page if the vertical position exceeds the margin.

---

### **9. `draw_row`**

Draws a row of data across columns:

- Wraps text for each column based on its width.
- Iterates through the wrapped lines and places text in the respective column positions.
- Adds a divider between columns if applicable.
- Moves to the next line and adds a new page if the vertical position exceeds the margin.

---

### **10. `cell`**

Places text in a single cell:

- Adds text at the current vertical position.
- Moves to the next line and adds a new page if the vertical position exceeds the margin.

---

### **11. `add_header`**

Adds a header with a separator line below it:

- Sets a larger font size for the header text.
- Adds the header text and a separator line.
- Resets the font size and moves to the next line.

---

### **12. `output`**

Generates the final PDF file:

1. Adds any remaining content to the `pages` list.
2. Constructs the PDF header (`%PDF-1.4`).
3. Creates font, page content, page, pages root, and catalog objects.
4. Builds the cross-reference table (`xref`) and trailer.
5. Writes the binary PDF data to the specified file.

---

### **13. `_escape`**

Escapes special characters in text to ensure proper rendering in the PDF.

---

### **Key Features**

- **Dynamic Layout**: Supports dynamic margins, font sizes, and text wrapping.
- **Column-Based Rendering**: Allows drawing rows and separators across multiple columns.
- **Minimal PDF Syntax**: Implements basic PDF syntax for text rendering and page structure.

---

### **Usage Example**

```python
pdf = MinimalPDF("example.pdf")
pdf.set_margin(40)
pdf.set_font(12)
pdf.add_header("Sample Header")
pdf.cell(0, 20, "This is a sample cell.")
pdf.add_page()
pdf.output()
```

This example creates a PDF with a header, a cell, and outputs the file.

---

### **Limitations**

- Does not support advanced PDF features like images, colors, or complex layouts.
- Assumes Helvetica font is available.

---

This class is ideal for simple PDF generation tasks where minimal dependencies are preferred.
