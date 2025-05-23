import http.client
import ssl
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your firewall details
hostname = os.getenv("FIREWALL_HOSTNAME")  # e.g., "192.168.29.55"
api_key = os.getenv("FIREWALL_API_KEY")  # Preloaded API key from .env file

if not hostname or not api_key:
    print("Error: FIREWALL_HOSTNAME or FIREWALL_API_KEY is not set in the .env file.")
    exit()

# Disable SSL verification (not recommended for production)
ssl_context = ssl._create_unverified_context()

# Function to send API requests


def send_request(endpoint, params):
    conn = http.client.HTTPSConnection(hostname, context=ssl_context)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    conn.request("POST", endpoint, params, headers)
    response = conn.getresponse()
    if response.status != 200:
        print(f"HTTP Error: {response.status} {response.reason}")
        conn.close()
        return None
    data = response.read()
    conn.close()
    return data


# Get user inputs for the rule
rule_name = input("Enter rule name: ").strip()  # AllowSSH
from_zone = input("Enter source zone: ").strip()  # any
to_zone = input("Enter destination zone: ").strip()  # any
source_ip = input("Enter source IP (or 'any'): ").strip() or "any"  # any
destination_ip = input(
    "Enter destination IP (or 'any'): ").strip() or "any"  # any
application = input("Enter application (or 'any'): ").strip() or "any"  # ssh
service = input("Enter service (or 'application-default' or 'any'): ").strip(
) or "application-default"  # application-default
action = input("Enter action (allow/deny/drop): ").strip().lower()  # allow

# Create the XML payload for the security rule
rule_payload = f"""
<entry name="{rule_name}">
    <from>
        <member>{from_zone}</member>
    </from>
    <to>
        <member>{to_zone}</member>
    </to>
    <source>
        <member>{source_ip}</member>
    </source>
    <destination>
        <member>{destination_ip}</member>
    </destination>
    <application>
        <member>{application}</member>
    </application>
    <service>
        <member>{service}</member>
    </service>
    <action>{action}</action>
</entry>
"""

# Add the rule to the firewall
print(f"Adding security rule '{rule_name}' to the firewall...")
# Adjust vsys if needed
xpath = "/config/devices/entry/vsys/entry[@name='vsys1']/rulebase/security/rules"
add_rule_params = f"type=config&action=set&xpath={xpath}&element={rule_payload}&key={api_key}"
add_rule_response = send_request("/api/", add_rule_params)
if add_rule_response is None:
    print("Failed to add the security rule.")
    exit()

# Parse the response to check for success
add_rule_tree = ET.fromstring(add_rule_response)
status = add_rule_tree.get("status")
if status == "success":
    print(f"✅ Rule '{rule_name}' created successfully.")
else:
    print(
        f"❌ Failed to create rule. Response: {ET.tostring(add_rule_tree, encoding='unicode')}")
