import json
import io
import xlsxwriter
import re


def create_excel(data, headers, file_name):
    """
    Create an Excel file from the given data and headers.
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format(
        {'bold': True, 'align': 'center', 'border': 1})
    col_widths = [len(header) for header in headers]

    # Write headers
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Write data
    for row, row_data in enumerate(data, start=1):
        for col, value in enumerate(row_data):
            worksheet.write(row, col, str(value))
            col_widths[col] = max(col_widths[col], len(str(value)))

    # Adjust column widths
    for col, width in enumerate(col_widths):
        worksheet.set_column(col, col, width + 2)

    workbook.close()
    output.seek(0)
    return output.read()


def process_input(input_text):
    """
    Process the input text and extract data based on JSON array or object patterns.
    """
    array_pattern = r'="(\[.*?\])"'
    object_pattern = r'Input="({.*})"'

    array_matches = re.findall(array_pattern, input_text)
    object_match = re.search(object_pattern, input_text)

    if array_matches and len(array_matches) > 1:
        # Process both arrays (value and regex)
        arrays = [json.loads(bytes(match, "utf-8").decode("unicode_escape"))
                  for match in array_matches]
        headers = ["Value", "Regex"]
        data = zip(arrays[0], arrays[1])  # Pair values and regex
        return headers, data
    elif array_matches:
        # Single array found
        json_str = bytes(array_matches[0], "utf-8").decode("unicode_escape")
        data = [[value] for value in json.loads(json_str)]
        headers = ["Values"]
        return headers, data
    elif object_match:
        json_str = bytes(object_match.group(
            1), "utf-8").decode("unicode_escape")
        data = json.loads(json_str)
        if isinstance(data, dict) and "Commands" in data:
            commands = data["Commands"]
            headers = list(commands[0].keys())
            data = [[cmd.get(header, "") for header in headers]
                    for cmd in commands]
            return headers, data
        else:
            raise ValueError("Unsupported JSON structure.")
    else:
        fallback_match = re.search(r'(\{.*\}|\[.*\])', input_text)
        if fallback_match:
            json_str = bytes(fallback_match.group(
                1), "utf-8").decode("unicode_escape")
            data = json.loads(json_str)
            if isinstance(data, list):
                headers = ["Values"]
                data = [[value] for value in data]
                return headers, data
            else:
                raise ValueError("Unsupported JSON structure.")
        else:
            raise ValueError(
                "No valid JSON array or object found in the input string")


def main():
    # Defensive argument extraction and logging for XSOAR quirks
    args = demisto.args()
    demisto.info(f'Args received: {args}')
    input_text = args.get("input_text", "")
    if not input_text:
        input_text = next(iter(args.values()), "")
    if isinstance(input_text, (dict, list)):
        input_text = str(input_text)
    input_text = input_text.replace('\r\n', '\n')
    demisto.info(f'Input text: {input_text}')

    try:
        headers, data = process_input(input_text)
        filename = "rules_output.xlsx"
        excel_data = create_excel(data, headers, filename)

        # Attach file to War Room for users
        file_entry = fileResult(filename, excel_data)
        demisto.results(file_entry)

        # Put EntryID and name in context for playbook/automation chaining
        return_results(CommandResults(
            outputs_prefix="ExtractedRulesExcel",
            outputs={
                "EntryID": file_entry.get("FileID"),
                "Name": filename
            }
        ))
    except Exception as e:
        demisto.error(f"Error processing input: {e}")
        return_results(f"Error processing input: {str(e)}")


if __name__ in ("__builtin__", "builtins", "__main__"):
    main()
