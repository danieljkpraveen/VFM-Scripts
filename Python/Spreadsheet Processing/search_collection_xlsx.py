import pandas as pd


def load_xlsx_data(file_path):
    """
    Load an Excel file and extract 'Module' and 'Description' columns from all sheets.
    Returns a combined DataFrame with an additional 'Sheet' column.
    """
    try:
        # Read all sheets into a dictionary of DataFrames
        xls = pd.read_excel(file_path, sheet_name=None, skiprows=4)
        combined = []
        for sheet_name, df in xls.items():
            # Check if the required columns exist
            if 'Modules' in df.columns and 'Description' in df.columns:
                temp = df[['Modules', 'Description']].rename(
                    columns={'Modules': 'Module'}).copy()
                temp['Sheet'] = sheet_name
                combined.append(temp)
        if not combined:
            print(
                "The required columns ('Modules' and 'Description') are not present in any sheet.")
            return None
        return pd.concat(combined, ignore_index=True)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None


def search_data(data, query):
    """
    Search for a query in the 'Module' or 'Description' columns.
    """
    if data is None or data.empty:
        print("No data available to search.")
        return None

    # Perform case-insensitive search
    result = data[
        data['Module'].astype(str).str.contains(query, case=False, na=False) |
        data['Description'].astype(str).str.contains(
            query, case=False, na=False)
    ]
    return result


if __name__ == "__main__":
    # Path to the Excel file
    file_path = "collection_sheet.xlsx"

    # Load data from the Excel file
    data = load_xlsx_data(file_path)

    if data is not None:
        print("Data loaded successfully. Here's a preview:")
        print(data.head())

        # Prompt user for a search query
        query = input("Enter a search term (module name or description): ")
        search_results = search_data(data, query)

        if search_results is not None and not search_results.empty:
            print("Search results:")
            print(search_results)
        else:
            print("No matching results found.")
