# 🛡️ Threat Hunting Lab: UAC Bypass Detection with Wazuh + Sysmon + Atomic Red Team

This lab demonstrates how to simulate and detect a **UAC Bypass (MITRE T1548.002)** using `Invoke-AtomicRedTeam`, Sysmon logging, and Wazuh SIEM integration. It is designed as part of a practical cybersecurity portfolio focused on detection engineering and threat hunting.

---

## 🧰 Lab Overview

- **Simulation Technique**: UAC Bypass (T1548.002) via `fodhelper.exe`, `eventvwr.exe`, `SilentCleanup`, etc.
- **Detection Tools**:
  - [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) with [SwiftOnSecurity config](https://github.com/SwiftOnSecurity/sysmon-config)
  - [Wazuh](https://wazuh.com/)
  - Custom Sysmon rules in `ossec.conf` and `local_rules.xml`
- **Attack Emulation**: 
  - [APTSimulator](https://github.com/NextronSystems/APTSimulator)
  - [Atomic Red Team](https://github.com/redcanaryco/invoke-atomicredteam)

---

## ⚙️ Infrastructure

- `Wazuh Server` (Manager: `sunugakure`)
- `AD Controller`, `PA-FW`, `Kibana` (Optional in lab context)

---

## 📦 Installation Steps

### Sysmon Deployment

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/Mazuco/wazuh/refs/heads/main/sysmonconfig-export.xml -OutFile C:\Sysmon\sysmonconfig-export.xml
.\Sysmon.exe -accepteula -i sysmonconfig-export.xml
```

### Wazuh Configuration

**Add to `ossec.conf`:**

```xml
<localfile>
  <location>Microsoft-Windows-Sysmon/Operational</location>
  <log_format>eventchannel</log_format>
</localfile>
```

**Download Rules:**

```bash
curl -O https://raw.githubusercontent.com/Mazuco/wazuh/refs/heads/main/rules_sysmon.xml -o /var/ossec/ruleset/rules/0999-sysmon_rules.xml
chmod 650 /var/ossec/ruleset/rules/0999-sysmon_rules.xml
systemctl restart wazuh-manager
```

---

## ☣️ Simulating Attacks with Atomic Red Team

```powershell
IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing)
Install-AtomicRedTeam -getAtomics
Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1"
Invoke-AtomicTest T1548.002 -ShowDetailsBrief
Invoke-AtomicTest T1548.002
Invoke-AtomicTest T1548.002 -Cleanup
```

---

## 📊 Screenshots & Detections

### 🧠 Sysmon Log Sample

![Sysmon Event Viewer](wazuh-01-attomic.png)

### 📈 Detection via Wazuh - MITRE Mapping

![Wazuh MITRE Detection](wazuh-02-attomic.png)

### 🧾 Raw JSON Log in Wazuh

![Wazuh JSON Raw](wazuh-03-attomic.png)

---

## 🧠 MITRE Techniques Detected

| Technique | Tactic |
|----------|--------|
| T1548.002 | Privilege Escalation, Defense Evasion |
| T1112     | Modify Registry |

---

## 🔁 Next Steps

- Add detection for T1053 (Scheduled Tasks)
- Include Sigma rules integration
- Integrate TheHive or Cortex for incident response
- Send alerts to Slack/Telegram using Wazuh integration

---

## 📚 References

- [Atomic Red Team - Red Canary](https://github.com/redcanaryco/atomic-red-team)
- [Sysmon Config - SwiftOnSecurity](https://github.com/SwiftOnSecurity/sysmon-config)
- [MITRE ATT&CK - T1548.002](https://attack.mitre.org/techniques/T1548/002/)
- [Wazuh Rule Development Docs](https://documentation.wazuh.com)

---

## 👨‍💻 Author

Jordan Moran Cabello | [@jomoca](https://github.com/jomoca)
