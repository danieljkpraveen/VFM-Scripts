# MinimalPDF Documentation

The `MinimalPDF` class is a lightweight Python library for generating PDF files programmatically. This documentation explains how to use the class in detail, including an example usage snippet.

---

## **Getting Started**

### **Installation**

The `MinimalPDF` class is self-contained and does not require external dependencies. Simply include the `MinimalPDF` class in your Python project.

---

## **Basic Usage**

### **Creating a PDF**

To create a PDF, initialize the `MinimalPDF` class with the desired filename and optionally specify page dimensions and margins.

```python
pdf = MinimalPDF("example.pdf")
```

---

### **Setting Margins**

You can dynamically set the page margins using the `set_margin` method.

```python
pdf.set_margin(30)  # Set a custom margin of 30 points
```

---

### **Adding a Header**

Use the `add_header` method to add a header to the PDF. This method automatically adds a separator line below the header.

```python
pdf.add_header("Keys and Values")  # Add a header with the text "Keys and Values"
```

---

### **Defining Columns**

Columns can be defined dynamically as a list of tuples, where each tuple specifies the X position and width of the column.

```python
columns = [
    (pdf.margin, 200),  # Column 1: X position = margin, Width = 200
    (pdf.margin + 210, 200),  # Column 2: X position = margin + 210, Width = 200
]
```

---

### **Drawing Rows**

To add rows of data to the PDF, use the `draw_row` method. This method wraps text within columns and handles multi-line content automatically.

```python
divider = " | "  # Define a divider string between columns

for row in data:
    pdf.draw_row(row, columns, divider=divider)
```

---

### **Adding Separators**

You can add separator lines between rows using the `draw_separator` method.

```python
pdf.draw_separator(columns, divider=divider)
```

---

### **Outputting the PDF**

Once all content is added, use the `output` method to generate the PDF file.

```python
pdf.output()
print(f"[Local Dev] Saved file: {filename}")
```

---

## **Example Usage**

Below is a complete example of how to use the `MinimalPDF` class to create a PDF with dynamic columns and rows:

```python
def create_text_pdf(data, filename):
    pdf = MinimalPDF(filename)
    pdf.set_margin(30)  # Set a custom margin
    pdf.add_header("Keys and Values")  # Add a header

    # Define columns dynamically
    columns = [
        (pdf.margin, 200),  # Column 1: X position = margin, Width = 200
        (pdf.margin + 210, 200),  # Column 2: X position = margin + 210, Width = 200
    ]
    divider = " | "  # Define a divider string

    # Add rows and separators
    for row in data:
        pdf.draw_row(row, columns, divider=divider)
        pdf.draw_separator(columns, divider=divider)

    # Generate the PDF file
    pdf.output()
    print(f"[Local Dev] Saved file: {filename}")
```

### **Input Data**

The `data` parameter should be a list of lists, where each inner list represents a row of data. For example:

```python
data = [
    ["Key1", "Value1"],
    ["Key2", "Value2"],
    ["Key3", "Value3"],
]
```

### **Output**

The above example will generate a PDF file with two columns: "Keys" and "Values," and save it to the specified filename.

---

## **Advanced Features**

### **Custom Font Sizes**

You can change the font size dynamically using the `set_font` method.

```python
pdf.set_font(14)  # Set font size to 14 points
```

---

### **Multi-Page Support**

The `MinimalPDF` class automatically handles page breaks when the content exceeds the page height.

---

## **Limitations**

- Does not support advanced PDF features like images, colors, or complex layouts.
- Assumes Helvetica font is available.

---

## **Conclusion**

The `MinimalPDF` class is ideal for simple PDF generation tasks, such as creating tabular data or structured text documents. Its lightweight design makes it easy to integrate into any Python project.
