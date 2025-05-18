# 🔐 Wazuh File Integrity Monitoring Lab (Linux & Windows)

This lab demonstrates how to configure and validate **File Integrity Monitoring (FIM)** using **Wazuh** in both **Linux** and **Windows environments**, covering both centralized and local configurations.

---

## 🏗 Lab Architecture

| Hostname   | Role               | IP Address | OS / Platform       |
| ---------- | ------------------ | ---------- | ------------------- |
| Kumogakure | Wazuh Manager      | 10.1.3.11  | Ubuntu 20.04 LTS    |
| Uchiha     | Linux Agent        | 10.1.2.11  | Ubuntu 20.04 LTS    |
| Konoha     | Windows Agent (AD) | 10.1.1.X   | Windows Server 2022 |

---

## ✅ Linux Agent (Uchiha) - Centralized FIM Configuration

### 🔧 Configuration on Wazuh Manager

File: `/var/ossec/etc/shared/default/agent.conf`

```xml
<agent_config os="linux">
  <syscheck>
    <directories check_all="no" check_sum="yes">/root/fim-test</directories>
  </syscheck>
</agent_config>
```

### 📊 Validation Process

1. Restart syscheck for the Linux agent (ID: 004):

```bash
sudo /var/ossec/bin/agent_control -r -u 004
```

2. Create or modify a file to trigger FIM:

```bash
sudo mkdir -p /root/fim-test
echo "Test FIM Event $(date)" > /root/fim-test/fimtestfile.txt
```

3. Confirm detection in Wazuh Manager:

```bash
tail -f /var/ossec/logs/alerts/alerts.json | grep fimtestfile
```

### 🔍 Example Output:

```json
{
  "rule": {
    "id": "550",
    "description": "Integrity checksum changed.",
    "mitre": {
      "id": ["T1565.001"],
      "tactic": ["Impact"],
      "technique": ["Stored Data Manipulation"]
    }
  },
  "syscheck": {
    "path": "/root/fim-test/fimtestfile.txt",
    "md5_before": "...",
    "md5_after": "...",
    "event": "modified"
  },
  "location": "syscheck"
}
```

### 🖼 Screenshot

![Linux FIM - Uchiha](images/wazuh-Uchiha.png)

---

## ✅ Windows Agent (Konoha - Active Directory) - Local FIM Configuration

### 🔧 Configuration in `ossec.conf` (Local to Agent)

```xml
<ossec_config>
  <syscheck>
    <directories check_all="no" check_sum="yes" realtime="yes">C:\fim-test</directories>
  </syscheck>
</ossec_config>
```

### 📊 Validation Process

1. Restart agent:

```powershell
Stop-Service -Name "WazuhSvc"
Start-Service -Name "WazuhSvc"
```

2. Create or edit test file:

```powershell
echo "FIM Windows Test" > C:\fim-test\fimtestfile.txt
```

3. Check for alert in Wazuh Dashboard or verify via alerts.json on the manager.

### 🖼 Screenshot

![Windows FIM - Konoha](images/wazuh-Konoha.png)

---

## 💡 Summary Table

| Feature             | Linux Agent (Uchiha)            | Windows Agent (Konoha)       |
| ------------------- | ------------------------------- | ---------------------------- |
| Configuration Type  | Centralized (shared/agent.conf) | Local (agent ossec.conf)     |
| Manual FIM Scan     | `agent_control -r -u 004`       | Restart WazuhSvc             |
| Realtime Monitoring | Optional                        | Enabled via `realtime` attr. |
| Visibility          | alerts.json / Dashboard         | Dashboard / alerts.json      |
| Event Rule ID       | 550                             | 550                          |
| MITRE Mapping       | T1565.001                       | T1565.001                    |

---

## 📚 References

* [Wazuh File Integrity Monitoring](https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html)
* [Wazuh Agent Shared Config](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/agent-config.html)
* [Wazuh Ruleset - Rule 550](https://documentation.wazuh.com/current/user-manual/ruleset/rules.html#rule-550)

---

