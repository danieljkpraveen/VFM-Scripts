import os
import csv
from xml.etree import ElementTree as ET
from dotenv import load_dotenv
from panos.firewall import Firewall
from tabulate import tabulate


load_dotenv()

# Replace with your firewall details
hostname = os.getenv("hostname")
username = os.getenv("username")
password = os.getenv("password")
api_key = os.getenv("api_key")

# Connect to the firewall
print("Connecting to the firewall...")
fw = Firewall(hostname, api_key=api_key)
# fw = Firewall(hostname, username, password)

# Available log types (from PAN-OS CLI documentation)
valid_log_types = [
    "traffic", "threat", "url", "wildfire", "data",
    "config", "system", "hipmatch", "gpc", "iptag",
    "tunnel", "alarm", "auth", "user-id", "decryption", "unified"
]

# Get user input
print("Available log types:")
for name in valid_log_types:
    print(f"- {name}")

log_type_input = input("\nEnter log type ('all' to display all logs): ").strip().lower()
log_limit_input = input("Enter number of logs to fetch: ")
log_limit = int(log_limit_input) if log_limit_input.isdigit() else 10

start_time = input("Start time (YYYY/MM/DD HH:MM:SS): ").strip()
end_time = input("End time (YYYY/MM/DD HH:MM:SS): ").strip()

# Determine which log types to fetch
if log_type_input == "all":
    log_types = valid_log_types
elif log_type_input in valid_log_types:
    log_types = [log_type_input]
else:
    print(f"Invalid log type: {log_type_input}")
    exit(1)

for log_type in log_types:
    print(f"\nFetching {log_type} logs...")

    cmd = (
        f"show log {log_type} direction equal forward "
        f"time {start_time} to {end_time} max {log_limit}"
    )

    try:
        xml_response = fw.op(cmd, cmd="show")
        root = ET.fromstring(xml_response)
        entries = root.findall(".//entry")

        if not entries:
            print("No log entries found.")
            continue

        # Dynamically extract field names using full loop
        field_names_set = set()
        for entry in entries:
            for elem in entry:
                field_names_set.add(elem.tag)

        field_names = sorted(list(field_names_set))

        # Build table rows
        table = []
        for entry in entries:
            row = []
            for field in field_names:
                value = entry.findtext(field, default="-")
                row.append(value)
            table.append(row)

        # Display in terminal
        print(tabulate(table, headers=field_names, tablefmt="grid"))

        # Write to CSV file per log type
        filename = f"{log_type}_logs.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(field_names)
            writer.writerows(table)

        print(f"Logs exported to: {filename}")

    except Exception as e:
        print(f"Error fetching {log_type} logs: {e}")
