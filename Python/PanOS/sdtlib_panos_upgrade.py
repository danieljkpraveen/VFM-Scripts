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

auth_tree = ET.fromstring(auth_response)
api_key = auth_tree.find(".//key").text
print("Authentication successful. API key obtained.")

# Check if the firewall is active in HA
print("Checking HA status...")
ha_status_params = f"type=op&cmd=<show><high-availability><state/></high-availability></show>&key={api_key}"
ha_status_response = send_request("/api/", ha_status_params)
if ha_status_response is None:
    print("Failed to check HA status.")
    exit()

ha_tree = ET.fromstring(ha_status_response)
ha_state = ha_tree.find(".//state").text
is_active = ha_state.lower() == "active"
print(f"Firewall HA state: {ha_state}")

# Backup configurations to an XML file
print("Backing up configurations...")
backup_params = f"type=export&category=configuration&key={api_key}"
backup_response = send_request("/api/", backup_params)
if backup_response is None:
    print("Failed to back up configurations.")
    exit()

with open("firewall_backup.xml", "wb") as backup_file:
    backup_file.write(backup_response)
print("Backup completed and saved as 'firewall_backup.xml'.")

# Function to fetch available upgrade versions


def fetch_upgrade_versions():
    print("Fetching available software versions...")
    info_params = f"type=op&cmd=<request><system><software><info/></software></system></request>&key={api_key}"
    info_response = send_request("/api/", info_params)
    if info_response is None:
        print("Failed to fetch software versions.")
        exit()

    info_tree = ET.fromstring(info_response)
    versions = []
    for entry in info_tree.findall(".//entry"):
        version = entry.find("version").text
        downloaded = entry.find("downloaded").text
        versions.append((version, downloaded))
    return versions

# Function to upgrade the firewall


def upgrade_firewall(target_version):
    print(f"Upgrading to PAN-OS version {target_version}...")
    download_params = f"type=op&cmd=<request><system><software><download><version>{target_version}</version></download></software></system></request>&key={api_key}"
    download_response = send_request("/api/", download_params)
    if download_response is None:
        print("Failed to download the software.")
        exit()
    print("Download completed.")

    install_params = f"type=op&cmd=<request><system><software><install><version>{target_version}</version></install></software></system></request>&key={api_key}"
    install_response = send_request("/api/", install_params)
    if install_response is None:
        print("Failed to install the software.")
        exit()
    print("Installation completed.")

    print("Rebooting the firewall...")
    reboot_params = f"type=op&cmd=<request><restart><system/></restart></request>&key={api_key}"
    reboot_response = send_request("/api/", reboot_params)
    if reboot_response is None:
        print("Failed to reboot the firewall.")
        exit()
    print("Firewall is rebooting.")


# Handle upgrade process based on HA state
if is_active:
    print("Firewall is active in HA. Upgrading passive firewall first...")
    # Switch to passive firewall (assuming hostname is updated for passive firewall)
    hostname = "192.168.29.56"  # Replace with passive firewall hostname
    print("Authenticating with the passive firewall...")
    auth_response = send_request("/api/", auth_params)
    if auth_response is None:
        print("Failed to authenticate with the passive firewall.")
        exit()

    auth_tree = ET.fromstring(auth_response)
    api_key = auth_tree.find(".//key").text
    print("Authentication successful with the passive firewall.")

    available_versions = fetch_upgrade_versions()
    print("\nAvailable PAN-OS Versions for Upgrade:")
    for version, downloaded in available_versions:
        status = "Downloaded" if downloaded == "yes" else "Not downloaded"
        print(f"- {version} ({status})")

    target_version = input(
        "\nEnter the version to upgrade the passive firewall to: ").strip()
    if not any(version == target_version for version, _ in available_versions):
        print(f"Version {target_version} not found among upgrade candidates.")
        exit()

    upgrade_firewall(target_version)

    # Switch back to active firewall
    hostname = "192.168.29.55"  # Replace with active firewall hostname
    print("Authenticating with the active firewall...")
    auth_response = send_request("/api/", auth_params)
    if auth_response is None:
        print("Failed to authenticate with the active firewall.")
        exit()

    auth_tree = ET.fromstring(auth_response)
    api_key = auth_tree.find(".//key").text
    print("Authentication successful with the active firewall.")

    upgrade_firewall(target_version)
else:
    print("Firewall is not active in HA. Proceeding with upgrade...")
    available_versions = fetch_upgrade_versions()
    print("\nAvailable PAN-OS Versions for Upgrade:")
    for version, downloaded in available_versions:
        status = "Downloaded" if downloaded == "yes" else "Not downloaded"
        print(f"- {version} ({status})")

    target_version = input("\nEnter the version to upgrade to: ").strip()
    if not any(version == target_version for version, _ in available_versions):
        print(f"Version {target_version} not found among upgrade candidates.")
        exit()

    upgrade_firewall(target_version)

# Load the backup configuration
print("Loading the backup configuration...")
load_params = f"type=import&category=configuration&key={api_key}"
with open("firewall_backup.xml", "rb") as backup_file:
    backup_data = backup_file.read()

conn = http.client.HTTPSConnection(hostname, context=ssl_context)
headers = {"Content-Type": "application/octet-stream"}
conn.request("POST", "/api/", backup_data, headers)
response = conn.getresponse()
if response.status != 200:
    print(
        f"Failed to load the backup configuration: {response.status} {response.reason}")
    conn.close()
    exit()
conn.close()
print("Backup configuration loaded successfully.")
