import http.client
import ssl
import xml.etree.ElementTree as ET

# Replace with your firewall details
hostname = "192.168.29.55"
username = "admin"
password = "P@ssw0rd"

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


# Authenticate and get API key
print("Authenticating with the firewall...")
auth_params = f"type=keygen&user={username}&password={password}"
auth_response = send_request("/api/", auth_params)
if auth_response is None:
    print("Failed to authenticate.")
    exit()

# Parse API key from the response
auth_tree = ET.fromstring(auth_response)
api_key = auth_tree.find(".//key").text
print("Authentication successful. API key obtained.")

# Check for available software updates
print("Checking for available software updates...")
check_params = f"type=op&cmd=<request><system><software><check/></software></system></request>&key={api_key}"
check_response = send_request("/api/", check_params)
if check_response is None:
    print("Failed to check for software updates.")
    exit()

# List available software versions
print("Fetching available software versions...")
info_params = f"type=op&cmd=<request><system><software><info/></software></system></request>&key={api_key}"
info_response = send_request("/api/", info_params)
if info_response is None:
    print("Failed to fetch software versions.")
    exit()

# Parse available versions from the response
info_tree = ET.fromstring(info_response)
available_versions = []
for entry in info_tree.findall(".//entry"):
    version = entry.find("version").text
    downloaded = entry.find("downloaded").text
    available_versions.append((version, downloaded))

if not available_versions:
    print("No upgrade candidates available.")
    exit()

# Display available upgrade versions
print("\nAvailable PAN-OS Versions for Upgrade:")
for version, downloaded in available_versions:
    status = "Downloaded" if downloaded == "yes" else "Not downloaded"
    print(f"- {version} ({status})")

# Prompt user to select a version
target_version = input("\nEnter the version to upgrade to: ").strip()

# Check if the selected version is valid
if not any(version == target_version for version, _ in available_versions):
    print(f"Version {target_version} not found among upgrade candidates.")
    exit()

# Download the selected version if not already downloaded
for version, downloaded in available_versions:
    if version == target_version and downloaded != "yes":
        print(f"Downloading PAN-OS version {target_version}...")
        download_params = f"type=op&cmd=<request><system><software><download><version>{target_version}</version></download></software></system></request>&key={api_key}"
        download_response = send_request("/api/", download_params)
        if download_response is None:
            print("Failed to download the software.")
            exit()
        print("Download completed.")
        break

# Install the downloaded version
print(f"Installing PAN-OS version {target_version}...")
install_params = f"type=op&cmd=<request><system><software><install><version>{target_version}</version></install></software></system></request>&key={api_key}"
install_response = send_request("/api/", install_params)
if install_response is None:
    print("Failed to install the software.")
    exit()
print("Installation completed.")

# Reboot the firewall
print("Rebooting the firewall to complete the upgrade...")
reboot_params = f"type=op&cmd=<request><restart><system/></restart></request>&key={api_key}"
reboot_response = send_request("/api/", reboot_params)
if reboot_response is None:
    print("Failed to reboot the firewall.")
    exit()
print("Upgrade process completed. Firewall is rebooting.")
