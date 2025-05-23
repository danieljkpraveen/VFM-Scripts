import os
import io
import pandas as pd
from O365 import Account, FileSystemTokenBackend

# MS365 credentials (use environment variables or a config file for security)
CLIENT_ID = os.getenv("O365_CLIENT_ID")
CLIENT_SECRET = os.getenv("O365_CLIENT_SECRET")
TOKEN_PATH = "o365_token.txt"

# Authenticate with MS365
credentials = (CLIENT_ID, CLIENT_SECRET)
token_backend = FileSystemTokenBackend(token_path='.', token_filename=TOKEN_PATH)
account = Account(credentials, token_backend=token_backend)
if not account.is_authenticated:
    account.authenticate(scopes=['basic', 'message_all', 'mailbox'])

# Get mailbox
mailbox = account.mailbox()

# User input for subject and attachment name
target_subject = input("Enter the subject of the email: ").strip()
attachment_name = input("Enter the exact name of the attachment (e.g., file.xlsx): ").strip()

# Search for the specific email by subject
inbox = mailbox.inbox_folder()
query = inbox.new_query().on_attribute('subject').equals(target_subject)
messages = inbox.get_messages(limit=20, query=query, download_attachments=True)

found_attachment = None
for message in messages:
    for att in message.attachments:
        if att.name == attachment_name:
            found_attachment = att
            break
    if found_attachment:
        break

if not found_attachment:
    print("Attachment not found with the given name in emails with the specified subject.")
    exit(1)

# Read the attachment into a DataFrame (supports Excel files)
attachment_bytes = io.BytesIO(found_attachment.content)
df = pd.read_excel(attachment_bytes)

# Write to CSV
output_csv = "output.csv"
df.to_csv(output_csv, index=False)
print(f"Spreadsheet extracted and saved to {output_csv}")