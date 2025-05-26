import csv
import re
import requests
from msal import PublicClientApplication

# Configuration for Microsoft Graph API
CLIENT_ID = 'your-client-id'  # Replace with your app's client ID
SCOPES = ['Mail.Read']  # Permission to read emails
CSV_FILE_PATH = 'output.csv'
EMAIL_SUBJECT_FILTER = 'Specific Subject'  # Replace with the subject to filter


def authenticate_outlook():
    """Authenticate with Microsoft Graph API for personal Outlook accounts."""
    app = PublicClientApplication(
        CLIENT_ID,
        authority="https://login.microsoftonline.com/common"
    )
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        result = app.acquire_token_interactive(SCOPES)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Authentication failed: " +
                        str(result.get("error_description")))


def get_emails(access_token):
    """Retrieve emails from the Microsoft Graph API."""
    url = "https://graph.microsoft.com/v1.0/me/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "$top": 10,  # Limit the number of emails retrieved
        "$select": "subject,bodyPreview,body",  # Select only relevant fields
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        raise Exception(
            f"Failed to fetch emails: {response.status_code} {response.text}")


def extract_email_content(email_body):
    """Extract relevant content from the email body."""
    # Use regex to extract rules from the email body
    rules = re.findall(r'Rules where .*?=\[.*?\]', email_body)
    extracted_data = []
    for rule in rules:
        key, values = rule.split('=', 1)
        key = key.strip()
        values = values.strip('[]').split(',')
        values = [v.strip().strip('"') for v in values]
        extracted_data.append([key] + values)
    return extracted_data


def save_to_csv(data, file_path):
    """Save extracted data to a CSV file."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Rule Description', 'Values'])
        for row in data:
            writer.writerow(row)


def main():
    # Authenticate and get an access token
    access_token = authenticate_outlook()

    # Retrieve emails
    emails = get_emails(access_token)

    for email in emails:
        subject = email.get("subject", "")
        body = email.get("body", {}).get("content", "")

        if EMAIL_SUBJECT_FILTER in subject:
            extracted_data = extract_email_content(body)
            save_to_csv(extracted_data, CSV_FILE_PATH)
            print(f"Data saved to {CSV_FILE_PATH}")
            break
    else:
        print("No matching email found.")


if __name__ == "__main__":
    main()
