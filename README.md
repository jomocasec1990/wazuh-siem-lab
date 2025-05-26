# 🧠 Wazuh SIEM Lab — Endpoint Telemetry, Threat Detection & Response Engineering

This repository showcases a structured, modular lab environment built on **Wazuh**, focused on simulating realistic enterprise monitoring, threat detection, and automated response use cases across Windows and Linux endpoints.

Rather than deploying a generic SIEM stack, this project is designed to **develop, test, and validate detection engineering techniques** using the native capabilities of Wazuh — including File Integrity Monitoring, Registry auditing, centralized agent management, malware behavior detection, custom rule sets, YARA scans, and Active Response.

The goal is not only to observe logs — but to **transform endpoint telemetry into actionable detection**, mimicking the workflows of real-world Security Operations Centers (SOCs).

---

## 🎯 What This Lab Covers

- 🔍 Endpoint-focused detection: Windows Registry, processes, file hashes, behavior indicators.
- ⚙️ Wazuh agent group management, remote configuration, rule inheritance and overrides.
- 📦 Threat intelligence integrations: **VirusTotal**, **AbuseIPDB**, **CDB lists**, and **YARA rules**.
- ⚔️ Simulation of malware techniques: Mirai, Xbash, LOLBins, USB abuse, and persistence.
- 🧠 Custom rules tied to **MITRE ATT&CK** and mapped to real tactics and techniques.
- 🚨 Active Response automation for malware containment and post-exploitation actions.
- 📊 Log enrichment and event correlation across multiple systems and layers.

---

## 🔬 Why This Lab Exists

Security tooling alone doesn't make a SOC effective. What matters is **how you tune detections, simulate threats, validate rules, and respond to alerts.**

This lab is designed to:
- Reproduce adversarial behavior in a controlled environment.
- Create and test custom detections based on behavior, not just indicators.
- Practice threat hunting with contextual telemetry and MITRE mappings.
- Gain deep, practical familiarity with Wazuh’s detection and response stack.

It’s an evolving project — each folder reflects a completed or in-progress capability, and will expand as more advanced topics (e.g., Sysmon, Yeti, Suricata, Zabbix) are added.

---

## 🗂️ Repository Layout

| Folder              | Description |
|---------------------|-------------|
| `02-File-Integrity` | File monitoring rules and tuning on Windows |
| `03-Create-Dashboard` | Dashboards, visualizations, Kibana-style views |
| `04-Linux-Audit`    | Linux agent telemetry and audit rules |
| `05-Defender`       | Defender integration and malware detection |
| `06-CDB-Lab`        | Hash-based detection using CDB list matching |
| *More directories coming soon...* |

---

## 🧠 Learn More

- [Wazuh Official Documentation](https://documentation.wazuh.com/)
- [Wazuh Ruleset Reference](https://documentation.wazuh.com/current/user-manual/ruleset/index.html)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Wazuh GitHub Repository](https://github.com/wazuh/wazuh)
