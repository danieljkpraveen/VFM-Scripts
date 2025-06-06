# Security Vulnerability Report for `./vulnerable.py`

This report summarizes all Bandit-detected vulnerabilities, with explanations and example malicious code to illustrate possible attacks.

---

## 1. Use of `subprocess` Module

- **Bandit ID:** B404:blacklist
- **Location:** Line 1
- **Severity:** Low
- **Explanation:**  
  The `subprocess` module allows running system commands from Python. If user input is passed unsafely, it can lead to command injection.

**Example Malicious Code:**

```python
import subprocess
user_input = "ls; rm -rf /"
subprocess.call(f"echo {user_input}", shell=True)  # Dangerous if user_input is not sanitized
```

---

## 2. Use of `pickle` Module

- **Bandit ID:** B403:blacklist
- **Location:** Line 2
- **Severity:** Low
- **Explanation:**  
  The `pickle` module can execute arbitrary code during deserialization. Never unpickle untrusted data.

**Example Malicious Code:**

```python
import pickle
malicious_pickle = b"cos\nsystem\n(S'ls /; rm -rf /'\ntR."
pickle.loads(malicious_pickle)  # This will run the system command!
```

---

## 3. `subprocess.call` with `shell=True`

- **Bandit ID:** B602:subprocess_popen_with_shell_equals_true
- **Location:** Line 7
- **Severity:** High
- **Explanation:**  
  Using `shell=True` with user input can allow arbitrary command execution (command injection).

**Example Malicious Code:**

```python
cmd = input("Enter command: ")  # user enters: "ls; rm -rf /"
subprocess.call(cmd, shell=True)  # Executes both ls and rm -rf /
```

---

## 4. Use of `eval()` on User Input

- **Bandit ID:** B307:blacklist
- **Location:** Line 11
- **Severity:** Medium
- **Explanation:**  
  `eval()` executes arbitrary Python code. Using it on user input allows code execution attacks.

**Example Malicious Code:**

```python
user_input = "__import__('os').system('rm -rf /')"
eval(user_input)  # Executes destructive command
```

---

## 5. Unsafe Deserialization with `pickle.loads()`

- **Bandit ID:** B301:blacklist
- **Location:** Line 15
- **Severity:** Medium
- **Explanation:**  
  Unpickling attacker-controlled data will execute code embedded in the pickle object.

**Example Malicious Code:**

```python
import pickle
# Attacker crafts a pickle object that runs code
malicious_pickle = b"cos\nsystem\n(S'echo hacked > /tmp/hacked'\ntR."
pickle.loads(malicious_pickle)
```

---

## 6. Hardcoded Password String

- **Bandit ID:** B105:hardcoded_password_string
- **Location:** Line 19
- **Severity:** Low
- **Explanation:**  
  Hardcoding passwords in code can lead to credential leaks if the code is leaked or shared.

**Example Malicious Code:**

```python
password = "SuperSecret123"  # If code is leaked, attacker gets password
```

---

## 7. Hardcoded Temporary File Path

- **Bandit ID:** B108:hardcoded_tmp_directory
- **Location:** Line 24
- **Severity:** Medium
- **Explanation:**  
  Using a fixed temporary file path can be exploited by a local attacker via race conditions or symlink attacks.

**Example Malicious Code:**

```python
with open("/tmp/my_tempfile", "w") as f:
    f.write("malicious content")
# Attacker creates a symlink at /tmp/my_tempfile pointing to /etc/passwd, causing privilege escalation
```

---

## 8. Use of `os.system` with User Input

- **Bandit ID:** B605:start_process_with_a_shell
- **Location:** Line 29
- **Severity:** High
- **Explanation:**  
  Passing user input to `os.system()` can allow arbitrary command injection.

**Example Malicious Code:**

```python
command = input("Enter command: ")  # user enters: "ls; rm -rf /"
os.system(command)  # Executes both ls and rm -rf /
```

---

## Summary Table

| Vulnerability               | CWE     | Severity | Example Malicious Code Location |
| --------------------------- | ------- | -------- | ------------------------------- |
| Use of subprocess           | CWE-78  | Low      | See 1, 3, 8                     |
| Use of pickle               | CWE-502 | Low/Med  | See 2, 5                        |
| subprocess.call(shell=True) | CWE-78  | High     | 3                               |
| eval() on user input        | CWE-78  | Medium   | 4                               |
| Hardcoded password          | CWE-259 | Low      | 6                               |
| Hardcoded tmp file          | CWE-377 | Medium   | 7                               |
| os.system with user input   | CWE-78  | High     | 8                               |

---

**Recommendations:**

- Never use `eval()` or `pickle.loads()` on untrusted data.
- Avoid passing user input directly to shell commands.
- Use secure temporary file handling (e.g., `tempfile` module).
- Store secrets securely, not in code.
- Prefer safer modules (e.g., `ast.literal_eval`, `subprocess.run` with argument lists).

---
