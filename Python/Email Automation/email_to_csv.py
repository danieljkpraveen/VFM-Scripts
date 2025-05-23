# The below version is using the O365 library
#
# import os
# from O365 import Account
# import pandas as pd
# from bs4 import BeautifulSoup
# from datetime import datetime
# from dotenv import load_dotenv

# def get_credentials():
#     load_dotenv()

#     return {
#         'client_id': os.getenv('MS365_CLIENT_ID'),
#         'client_secret': os.getenv('MS365_CLIENT_SECRET')
#     }

# def authenticate():
#     credentials = get_credentials()
#     account = Account((credentials['client_id'], credentials['client_secret']))

#     if not account.is_authenticated:
#         account.authenticate()

#     return account

# def extract_table_from_html(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     tables = soup.find_all('table')

#     if not tables:
#         return None

#     # Get the first table
#     table = tables[0]
#     data = []

#     # Extract headers
#     headers = []
#     for th in table.find_all('th'):
#         headers.append(th.text.strip())

#     if not headers:  # If no headers found, try first row
#         headers = [td.text.strip() for td in table.find('tr').find_all('td')]

#     # Extract rows
#     for row in table.find_all('tr')[1:]:  # Skip header row
#         row_data = [td.text.strip() for td in row.find_all('td')]
#         if row_data:
#             data.append(row_data)

#     return pd.DataFrame(data, columns=headers)

# def process_emails():
#     account = authenticate()
#     mailbox = account.mailbox()
#     inbox = mailbox.inbox_folder()

#     # Get unread messages
#     messages = inbox.get_messages(limit=10, query="isRead eq false")

#     for message in messages:
#         # Get email body
#         body = message.body

#         # Extract table data
#         df = extract_table_from_html(body)

#         if df is not None:
#             # Create filename based on email subject and date
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             safe_subject = "".join(x for x in message.subject if x.isalnum())[:30]
#             filename = f"extracted_table_{safe_subject}_{timestamp}.csv"

#             # Save to CSV
#             output_path = os.path.join('output', filename)
#             os.makedirs('output', exist_ok=True)
#             df.to_csv(output_path, index=False)

#             # Mark email as read
#             message.mark_as_read()

#             print(f"Processed email: {message.subject}")
#             print(f"Saved to: {output_path}")

# if __name__ == "__main__":
#     process_emails()

# The below version is using the msgraph sdk for python official library
import os
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv


def get_credentials():
    load_dotenv()
    return {
        'tenant_id': os.getenv('TENANT_ID'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET')
    }


def authenticate():
    credentials = get_credentials()
    credential = ClientSecretCredential(
        tenant_id=credentials['tenant_id'],
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret']
    )
    return GraphClient(credential=credential)


def extract_table_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')

    if not tables:
        return None

    # Get the first table
    table = tables[0]
    data = []

    # Extract headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    if not headers:  # If no headers found, try first row
        headers = [td.text.strip() for td in table.find('tr').find_all('td')]

    # Extract rows
    for row in table.find_all('tr')[1:]:  # Skip header row
        row_data = [td.text.strip() for td in row.find_all('td')]
        if row_data:
            data.append(row_data)

    return pd.DataFrame(data, columns=headers)


def process_emails():
    client = authenticate()

    # Get unread messages from inbox
    messages = client.get('/me/mailFolders/inbox/messages', params={
        '$filter': 'isRead eq false',
        '$top': 10,
        '$select': 'subject,body,id'
    }).json()

    for message in messages.get('value', []):
        # Get email body
        body = message['body']['content']

        # Extract table data
        df = extract_table_from_html(body)

        if df is not None:
            # Create filename based on email subject and date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_subject = "".join(
                x for x in message['subject'] if x.isalnum())[:30]
            filename = f"extracted_table_{safe_subject}_{timestamp}.csv"

            # Save to CSV
            output_path = os.path.join('output', filename)
            os.makedirs('output', exist_ok=True)
            df.to_csv(output_path, index=False)

            # Mark email as read
            client.patch(f"/me/messages/{message['id']}", json={
                'isRead': True
            })

            print(f"Processed email: {message['subject']}")
            print(f"Saved to: {output_path}")


if __name__ == "__main__":
    process_emails()
