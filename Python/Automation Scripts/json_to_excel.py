import json
import xlsxwriter
import re
import sys

try:
    # Read input from stdin
    raw_input = sys.stdin.read().strip()

    # Try to extract JSON array or object using regex
    array_pattern = r'="(\[.*?\])"'
    object_pattern = r'Input="({.*})"'

    json_str = None

    array_matches = re.findall(array_pattern, raw_input)
    object_match = re.search(object_pattern, raw_input)

    if array_matches and len(array_matches) > 1:
        # Process both arrays (value and regex)
        arrays = []
        for match in array_matches:
            arr = json.loads(bytes(match, "utf-8").decode("unicode_escape"))
            arrays.append(arr)
        # Write both arrays to Excel in separate columns
        workbook = xlsxwriter.Workbook('rules_output.xlsx')
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'border': 1})
        worksheet.write(0, 0, 'Value', header_format)
        worksheet.write(0, 1, 'Regex', header_format)
        max_len = max(len(arrays[0]), len(arrays[1]))
        max_widths = [len('Value'), len('Regex')]
        for row in range(max_len):
            for col in range(2):
                value = arrays[col][row] if row < len(arrays[col]) else ""
                worksheet.write(row + 1, col, value)
                max_widths[col] = max(max_widths[col], len(str(value)))
        for col, width in enumerate(max_widths):
            worksheet.set_column(col, col, width + 2)
        workbook.close()
        print("Excel file 'rules_output.xlsx' has been created successfully.")
    elif array_matches:
        # Only one array found, process as before
        json_str = array_matches[0]
        json_str = bytes(json_str, "utf-8").decode("unicode_escape")
        data = json.loads(json_str)
        workbook = xlsxwriter.Workbook('rules_output.xlsx')
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'border': 1})
        worksheet.write(0, 0, 'Values', header_format)
        max_width = len('Values')
        for row, rule in enumerate(data, start=1):
            value = str(rule)
            worksheet.write(row, 0, value)
            max_width = max(max_width, len(value))
        worksheet.set_column(0, 0, max_width + 2)
        workbook.close()
        print("Excel file 'rules_output.xlsx' has been created successfully.")
    elif object_match:
        json_str = object_match.group(1)
        json_str = bytes(json_str, "utf-8").decode("unicode_escape")
        data = json.loads(json_str)
        if isinstance(data, dict) and "Commands" in data:
            commands = data["Commands"]
            workbook = xlsxwriter.Workbook('rules_output.xlsx')
            worksheet = workbook.add_worksheet()
            header_format = workbook.add_format(
                {'bold': True, 'align': 'center', 'border': 1})
            headers = list(commands[0].keys())
            col_widths = [len(header) for header in headers]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            for row, cmd in enumerate(commands, start=1):
                for col, header in enumerate(headers):
                    value = str(cmd.get(header, ""))
                    worksheet.write(row, col, value)
                    col_widths[col] = max(col_widths[col], len(value))
            for col, width in enumerate(col_widths):
                worksheet.set_column(col, col, width + 2)
            workbook.close()
            print("Excel file 'rules_output.xlsx' has been created successfully.")
        else:
            print("Unsupported JSON structure.")
    else:
        fallback_match = re.search(r'(\{.*\}|\[.*\])', raw_input)
        if fallback_match:
            json_str = fallback_match.group(1)
            json_str = bytes(json_str, "utf-8").decode("unicode_escape")
            data = json.loads(json_str)
            if isinstance(data, list):
                workbook = xlsxwriter.Workbook('rules_output.xlsx')
                worksheet = workbook.add_worksheet()
                header_format = workbook.add_format(
                    {'bold': True, 'align': 'center', 'border': 1})
                worksheet.write(0, 0, 'Values', header_format)
                max_width = len('Values')
                for row, rule in enumerate(data, start=1):
                    value = str(rule)
                    worksheet.write(row, 0, value)
                    max_width = max(max_width, len(value))
                worksheet.set_column(0, 0, max_width + 2)
                workbook.close()
                print("Excel file 'rules_output.xlsx' has been created successfully.")
            else:
                print("Unsupported JSON structure.")
        else:
            print("No valid JSON array or object found in the input string")
except Exception as e:
    print(f"An error occurred: {e}")
