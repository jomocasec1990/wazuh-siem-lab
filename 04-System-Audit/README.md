
# 🛡️ Wazuh Auditd Monitoring Lab (Linux)

This lab demonstrates how to monitor command execution on a Linux endpoint using **auditd** rules and **Wazuh**'s audit module.

---

## 📌 Objective

Track sensitive command usage (like `ls`, `cat`, `nano`, etc.) by non-root users using auditd and ingest logs into Wazuh for detection and correlation with MITRE ATT&CK.

---

## 🏗️ Lab Architecture

| Hostname   | Role          | IP          | OS              |
|------------|---------------|-------------|------------------|
| Kumogakure | Wazuh Manager | 10.1.3.11   | Ubuntu 20.04 LTS |
| Uchiha     | Linux Agent   | 10.1.2.11   | Ubuntu 20.04 LTS |

---

## 📦 Install auditd (Linux Agent - Uchiha)

Make sure `auditd` is installed and running:

```bash
sudo apt updates
sudo apt install auditd 
sudo systemctl enable auditd
sudo systemctl start auditd
```

## ⚙️ Agent Configuration (Uchiha)

### 1️⃣ Configure auditd rules

File: `/etc/audit/rules.d/audit.rules`

```bash
-D
-b 8192
--backlog_wait_time 0
-f 1

-a exit,always -F euid=1000 -F arch=b32 -S execve -k audit-wazuh-c
-a exit,always -F euid=1000 -F arch=b64 -S execve -k audit-wazuh-c
```

> Replace `1000` with your target user’s UID. You can find it with:
```bash
id -u jomoca
```

### 2️⃣ Load the audit rules

```bash
sudo augenrules --load
```

### 3️⃣ Validate active rules

```bash
sudo auditctl -l | grep audit-wazuh-c
```

Expected output:

```bash
-a always,exit -F arch=b32 -S execve -F euid=1000 -F key=audit-wazuh-c
-a always,exit -F arch=b64 -S execve -F euid=1000 -F key=audit-wazuh-c
```

---

## 📥 Wazuh Agent Configuration

File: `/var/ossec/etc/ossec.conf`

Append:

```xml
<localfile>
  <log_format>audit</log_format>
  <location>/var/log/audit/audit.log</location>
</localfile>
```

Then restart the agent:

```bash
sudo systemctl restart wazuh-agent
```

---

## 🧪 Test Execution

As the user being monitored (`jomoca`):

```bash
ls /etc/shadow
cat /etc/passwd
whoami
```

---

## 🔍 Expected Detection in Wazuh

Tail this log from the **Wazuh Manager**:

```bash
sudo tail -f /var/ossec/logs/alerts/alerts.json | grep audit-wazuh-c
```

Example:

```json
"rule": {
  "level": 3,
  "description": "Audit: Command: /usr/bin/grep.",
  "id": "80792",
  ...
},
"syscheck": {
  "path": "/usr/bin/grep",
  ...
},
"decoder": { "parent": "auditd", "name": "auditd" },
"data": {
  "audit": {
    "type": "SYSCALL",
    "command": "grep",
    "key": "audit-wazuh-c",
    ...
  }
}
```

---

## 📸 Screenshots

### Linux Agent Detection (Uchiha)

![Linux agent detection](wazuh-Uchiha.png)

### Windows Agent (Konoha) — From Previous FIM Lab

![Windows agent FIM](wazuh-konoha.png)

---

## 🧠 Summary Table

| Component      | Value                                    |
|----------------|------------------------------------------|
| Audit Tool     | auditd                                   |
| Rule Trigger   | Command execution (`execve` syscall)     |
| Rule Key       | `audit-wazuh-c`                          |
| Wazuh Module   | `logcollector` + `audit` decoder         |
| Rule ID        | 80792 (default rule for auditd command)  |
| MITRE ATT&CK   | T1059 (Command and Scripting Interpreter) |

---

## 📚 References

- [Wazuh - Audit log analysis](https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/operating-systems/linux/audit.html)
- [MITRE T1059](https://attack.mitre.org/techniques/T1059/)

---

## ✅ Status

Auditd monitoring configured and validated via Wazuh on Ubuntu agent.
