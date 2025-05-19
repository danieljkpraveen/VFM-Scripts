from panos.firewall import Firewall
from panos.policies import Rulebase, SecurityRule

# Connect to the firewall
hostname = "192.168.29.55"
username = "admin"
password = "P@ssw0rd"
# api_key = "YOUR_API_KEY"

# Connect to the firewall
print("Connecting to the firewall...")
# fw = Firewall(hostname, api_key=api_key)
fw = Firewall(hostname, username, password)

rulebase = fw.add(Rulebase())

# Get user inputs for the rule
rule_name = input("Enter rule name: ").strip() # AllowSSH
from_zone = input("Enter source zone: ").strip() # any
to_zone = input("Enter destination zone: ").strip() # any
source_ip = input("Enter source IP (or 'any'): ").strip() or "any" # any
destination_ip = input("Enter destination IP (or 'any'): ").strip() or "any" # any
application = input("Enter application (or 'any'): ").strip() or "any" # ssh
service = input("Enter service (or 'application-default' or 'any'): ").strip() or "application-default" # application-default
action = input("Enter action (allow/deny/drop): ").strip().lower() # allow

# Create rule object
rule = SecurityRule(
    name=rule_name,
    fromzone=[from_zone],
    tozone=[to_zone],
    source=[source_ip],
    destination=[destination_ip],
    application=[application],
    service=[service],
    action=action
)

# Attach to firewall and apply
# fw.add(rule)

try:
    # rule.apply()  # or use rule.create() if preferred
    rulebase.add(rule)
    rule.create()
    print(f"✅ Rule '{rule_name}' created successfully.")
except Exception as e:
    print(f"❌ Failed to create rule: {e}")

# rulebase.add(rule)
# rule.create()
