import subprocess
import pickle
import os

def execute_command(cmd):
    # B602: Subprocess with shell=True
    subprocess.call(cmd, shell=True)

def insecure_eval(user_input):
    # B307: Use of eval
    eval(user_input)

def insecure_pickle_loads(serialized_data):
    # B301: Pickle deserialization
    return pickle.loads(serialized_data)

def hardcoded_password():
    # B105: Hardcoded password string
    password = "SuperSecret123"
    return password

def write_temp_file(user_input):
    # B108: Hardcoded tmp file, potential race condition
    with open("/tmp/my_tempfile", "w") as f:
        f.write(user_input)

def use_os_system(command):
    # B605: os.system with user input
    os.system(command)
