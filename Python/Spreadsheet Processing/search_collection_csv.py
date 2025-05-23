import pandas as pd


def load_csv_data(file_path):
    """
    Load a CSV file and extract 'Module' and 'Description' columns.
    """
    try:
        # Read the CSV file, skipping the first 4 rows and using the 5th row as the header
        csv_data = pd.read_csv(file_path, skiprows=4)

        # Check if the required columns exist
        if 'Modules' in csv_data.columns and 'Description' in csv_data.columns:
            return csv_data[['Modules', 'Description']].rename(columns={'Modules': 'Module'}).reset_index(drop=True)
        else:
            print("The required columns ('Modules' and 'Description') are not present in the CSV file.")
            return None
    except Exception as e:
        print(f"Error loading CSV file: {e}")
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
        data['Module'].str.contains(query, case=False, na=False) |
        data['Description'].str.contains(query, case=False, na=False)
    ]
    return result


if __name__ == "__main__":
    # Path to the CSV file
    file_path = "panos_collection.csv"

    # Load data from the CSV file
    data = load_csv_data(file_path)

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
