from netmiko import ConnectHandler

device = {
    "device_type": "paloalto_panos",
    "host": "192.168.29.55",
    "username": "admin",
    "password": "P@ssw0rd",
}

print("\nConnecting to the firewall via SSH...")
ssh = ConnectHandler(**device)
print("✅ SSH connected!")

log_type = input("Enter log type: ")

# Disable pagination and scripting prompts
ssh.send_command_timing("set cli scripting-mode on")
ssh.send_command_timing("set cli pager off")

# Use send_command_timing to manually fetch the output
output = ssh.send_command_timing(f"show log {log_type}")

print("\n📄 System Info Output:")
print(output if output.strip() else "(Empty output received)")

ssh.disconnect()
