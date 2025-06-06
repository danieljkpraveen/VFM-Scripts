import PyPDF2

# Open the PDF file
file_path = "example.pdf"
with open(file_path, "rb") as pdf_file:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(pdf_file)

    # Check if metadata exists
    if reader.metadata:
        metadata = reader.metadata
        for key, value in metadata.items():
            print(f"{key}: {value}")
    else:
        print("No metadata found in the PDF file.")
