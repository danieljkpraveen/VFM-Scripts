import time
import requests
import urllib3
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote_plus

# Disable only the insecure request warning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FIREWALL_HOST = "192.168.29.55"
USERNAME = "admin"
PASSWORD = "P@ssw0rd"

def get_api_key():
    """ This function uses url and data to send a post request to the firewall
    and accepts an xml response. If key in response is none - API key is not
    found. Else it returns API key.
    """
    url = f"{FIREWALL_HOST}/api/"
    data = {
        "type": "keygen",
        "user": USERNAME,
        "password": PASSWORD
    }
    resp = requests.post(
        url,
        data=urlencode(data),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        verify=False,
        timeout=10
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    key = root.find(".//key")
    if key is None:
        raise Exception(f"API key not found in response:\n{resp.text}")
    return key.text

def run_op_cmd(api_key, cmd_xml):
    """ This function makes a get request to the firewall using api_key and cmd_xml.
    If response status is not 200 - API call has failed, else it returns the response text.
    """
    cmd_encoded = quote_plus(cmd_xml) # quote_plus() replaces empty strings with + and % symbols
    url = f"{FIREWALL_HOST}/api/?type=op&key={api_key}&cmd={cmd_encoded}"
    resp = requests.get(url, verify=False, timeout=10)
    resp.raise_for_status()
    return ET.fromstring(resp.text)

def get_content_versions(api_key):
    """ This function calls the ru_op_cmd() to make a API request that executes the cmd
    to retrieve current content version for Antivirus, URL Filtering, and Threat Prevention.
    """
    cmd = "<request><content><upgrade><info></info></upgrade></content></request>"
    root = run_op_cmd(api_key, cmd)

    content_keys = {
        "antivirus-version": "Antivirus",
        "url-filtering-version": "URL Filtering",
        "threats-version": "Threat Prevention",
    }

    versions = {}
    for key in content_keys:
        name = content_keys[key]
        elem = root.find(f".//{key}")
        if elem is not None and elem.text:
            versions[name] = elem.text
        else:
            versions[name] = "Not Installed / Unknown"
    return versions

def check_new_content_versions(api_key):
    """ This function calls the ru_op_cmd() to make a API request that executes the cmd
    to check if there is and update for content versions Antivirus, URL Filtering, and 
    Threat Prevention.
    """
    cmd = "<request><content><upgrade><check></check></upgrade></content></request>"
    root = run_op_cmd(api_key, cmd)

    updates = {}
    for content_type in ["antivirus", "url-filtering", "threats"]:
        elem = root.find(f".//{content_type}/version")
        if elem is not None and elem.text:
            updates[content_type] = elem.text
        else:
            updates[content_type] = None
    return updates

def trigger_content_install(api_key):
    """ This function calls the ru_op_cmd() to make a API request that executes the cmd
    to new content version updates.
    """
    cmd = "<request><content><upgrade><download></download></upgrade></content></request>"
    root = run_op_cmd(api_key, cmd)

    status = root.find(".//msg")
    if status is not None:
        return status.text
    else:
        return "Content update triggered, no detailed status returned."

def wait_for_update_completion(api_key, timeout=600, poll_interval=15):
    """ This function calls the ru_op_cmd() to make a API request that executes the cmd
    that periodically checks if content update has completed and retrys for 10mins with
    15sec breaks.
    """   
    # timout is the retry time limit (10mins/600secs) poll_interval is the pause
    # before next retry (15secs)
    elapsed = 0
    print("Waiting for content update to complete...")
    while elapsed < timeout:
        cmd = "<request><content><upgrade><info></info></upgrade></content></request>"
        root = run_op_cmd(api_key, cmd)

        # The update state is inside <status> element, typically "downloaded" or "idle"
        status_elem = root.find(".//status")
        if status_elem is not None:
            status = status_elem.text.lower()
            print(f"Current update status: {status}")
            if status in ["idle", "downloaded"]:
                # 'idle' means no ongoing update, 'downloaded' means update ready
                return True
        time.sleep(poll_interval)
        elapsed += poll_interval

    print("Timeout reached while waiting for content update.")
    return False

if __name__ == "__main__":
    print("Connecting to firewall and retrieving API key...")
    api_key = get_api_key()

    print("\nInstalled Content Versions:")
    installed_versions = get_content_versions(api_key)
    for name, ver in installed_versions.items():
        print(f"{name}: {ver}")

    print("\nChecking for new content versions...")
    new_versions = check_new_content_versions(api_key)
    updates_available = False
    for k, v in new_versions.items():
        installed = installed_versions.get(k.replace('-', ' ').title(), "Unknown")
        if v is not None:
            print(f"{k}: New version available: {v}")
            updates_available = True
        else:
            print(f"{k}: No new version available.")

    if not updates_available:
        print("\nAll content is up to date. No update needed.")
    else:
        print("\nTriggering content update...")
        result = trigger_content_install(api_key)
        print(f"Result: {result}")

        # Wait for update to complete (poll status)
        if wait_for_update_completion(api_key):
            print("\nUpdate completed. Fetching new installed versions...")
            final_versions = get_content_versions(api_key)
            for name, ver in final_versions.items():
                print(f"{name}: {ver}")
        else:
            print("Update did not complete within the expected time.")
