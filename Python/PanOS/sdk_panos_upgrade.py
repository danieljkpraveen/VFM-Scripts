from panos.firewall import Firewall
from panos.errors import PanDeviceError
import xml.etree.ElementTree as ET

# Replace with your firewall details
active_firewall_ip = "192.168.29.55"
passive_firewall_ip = "192.168.29.56"
username = "admin"
password = "P@ssw0rd"

# Function to connect to a firewall


def connect_to_firewall(ip):
    try:
        fw = Firewall(ip, username, password)
        fw.refresh_system_info()  # polulates object(fw) with the most recent system information
        print(f"Connected to firewall at {ip}")
        return fw
    except PanDeviceError as e:
        print(f"Failed to connect to firewall at {ip}: {e}")
        exit()

# Function to check HA state


def check_ha_state(fw):
    try:
        ha_status = fw.op("show high-availability state", xml=True)
        ha_tree = ET.fromstring(ha_status)
        ha_state = ha_tree.find(".//state").text
        print(f"Firewall HA state: {ha_state}")
        return ha_state.lower() == "active"  # return True if ha, False if standalone
    except PanDeviceError as e:
        print(f"Failed to check HA state: {e}")
        exit()

# Function to back up configurations


def backup_config(fw, backup_file):
    try:
        print("Backing up configurations...")
        config = fw.op(
            "<show><config><running></running></config></show>", xml=True)
        with open(backup_file, "wb") as file:
            file.write(config)
        print(f"Backup completed and saved as '{backup_file}'")
    except PanDeviceError as e:
        print(f"Failed to back up configurations: {e}")
        exit()

# Function to fetch available upgrade versions


def fetch_upgrade_versions(fw):
    try:
        software_info = fw.op("request system software info", xml=True)
        info_tree = ET.fromstring(software_info)
        versions = []
        for entry in info_tree.findall(".//entry"):
            version = entry.find("version").text
            downloaded = entry.find("downloaded").text
            versions.append((version, downloaded))
        return versions
    except PanDeviceError as e:
        print(f"Failed to fetch software versions: {e}")
        exit()

# Function to upgrade the firewall


def upgrade_firewall(fw, target_version):
    try:
        print(f"Upgrading to PAN-OS version {target_version}...")
        fw.software.download(target_version)
        print("Download completed.")
        fw.software.install(target_version)
        print("Installation completed.")
        print("Rebooting the firewall...")
        fw.restart()
        print("Firewall is rebooting.")
    except PanDeviceError as e:
        print(f"Failed to upgrade the firewall: {e}")
        exit()

# Function to load backup configuration


def load_backup_config(fw, backup_file):
    try:
        print("Loading the backup configuration...")
        # Use the file path directly in the operational command
        fw.op(
            f"<load><config><from>{backup_file}</from></config></load>", xml=True)
        print("Backup configuration loaded successfully.")
    except PanDeviceError as e:
        print(f"Failed to load the backup configuration: {e}")
        exit()


# Main logic
backup_file = "firewall_backup.xml"

# Connect to the active firewall
active_fw = connect_to_firewall(active_firewall_ip)

# Check if the active firewall is in HA
is_active = check_ha_state(active_fw)

# Back up the configuration
backup_config(active_fw, backup_file)

if is_active:
    print("Firewall is active in HA. Upgrading passive firewall first...")
    # Connect to the passive firewall
    passive_fw = connect_to_firewall(passive_firewall_ip)

    # Fetch available upgrade versions for the passive firewall
    available_versions = fetch_upgrade_versions(passive_fw)
    print("\nAvailable PAN-OS Versions for Upgrade:")
    for version, downloaded in available_versions:
        status = "Downloaded" if downloaded == "yes" else "Not downloaded"
        print(f"- {version} ({status})")

    # Get target version from the user
    target_version = input(
        "\nEnter the version to upgrade the passive firewall to: ").strip()
    if not any(version == target_version for version, _ in available_versions):
        print(f"Version {target_version} not found among upgrade candidates.")
        exit()

    # Upgrade the passive firewall
    upgrade_firewall(passive_fw, target_version)

    # Upgrade the active firewall
    print("Upgrading the active firewall...")
    upgrade_firewall(active_fw, target_version)
else:
    print("Firewall is not active in HA. Proceeding with upgrade...")
    # Fetch available upgrade versions for the active firewall
    available_versions = fetch_upgrade_versions(active_fw)
    print("\nAvailable PAN-OS Versions for Upgrade:")
    for version, downloaded in available_versions:
        status = "Downloaded" if downloaded == "yes" else "Not downloaded"
        print(f"- {version} ({status})")

    # Get target version from the user
    target_version = input("\nEnter the version to upgrade to: ").strip()
    if not any(version == target_version for version, _ in available_versions):
        print(f"Version {target_version} not found among upgrade candidates.")
        exit()

    # Upgrade the active firewall
    upgrade_firewall(active_fw, target_version)

# Load the backup configuration
load_backup_config(active_fw, backup_file)
