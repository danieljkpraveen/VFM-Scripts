import json
import xlsxwriter
import re
import sys

try:
    # Input string with extra characters
    raw_input = sys.stdin.read().strip()

    # Extract the JSON array using improved regex
    pattern = r'value="\[(.*?)\]"'
    match = re.search(pattern, raw_input)

    if match:
        # Reconstruct proper JSON array string
        json_str = '[' + match.group(1) + ']'

        # Clean up escaped quotes if present
        json_str = json_str.replace('\\"', '"')

        try:
            # Parse JSON string to Python list
            data = json.loads(json_str)

            # Create a new Excel workbook and worksheet
            workbook = xlsxwriter.Workbook('rules_output.xlsx')
            worksheet = workbook.add_worksheet()

            # Add header format - now just bold without background color
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'border': 1
            })

            # Write single header
            headers = ['Values']
            worksheet.write(0, 0, headers[0], header_format)

            # Track column width starting with header length
            max_width = len(headers[0])

            # Write data to Excel
            for row, rule in enumerate(data, start=1):
                worksheet.write(row, 0, rule)
                # Update max width if needed
                max_width = max(max_width, len(rule))

            # Set column width with padding
            worksheet.set_column(0, 0, max_width + 2)

            workbook.close()
            print("Excel file 'rules_output.xlsx' has been created successfully.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Attempted to parse: {json_str}")
    else:
        print("No valid JSON array found in the input string")
except Exception as e:
    print(f"An error occurred: {e}")
