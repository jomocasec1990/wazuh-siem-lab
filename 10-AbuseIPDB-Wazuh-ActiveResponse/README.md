# Wazuh + AbuseIPDB Integration with Active Response (SSH Brute Force Lab)

## 🔧 Lab Objective

This lab demonstrates how to integrate [AbuseIPDB](https://www.abuseipdb.com/) into a Wazuh environment to detect and actively block malicious SSH brute force attempts coming from public IP addresses with a high abuse score.

---

## ⚖️ Environment

* **Wazuh Manager:** `sunugakure`
* **Monitored Agent:** `Uzumaki` (IP: `10.1.2.12`)
* **Attacker (Kali):** Connected from a TOR IP (e.g., `185.220.101.1`)
* **SSH Port:** `22`
* **User Targeted:** `jomoca`

---

## 🖊️ Custom Rules (`/var/ossec/etc/rules/local_rules.xml`)

```xml
<group name="local,syslog,sshd,">
  <rule id="100002" level="5">
    <if_sid>5716</if_sid>
    <match type="pcre2">\b(?!(10)|192\.168|172\.(2[0-9]|1[6-9]|3[0-1])|(25[6-9]|2[6-9][0-9]|[3-9][0-9][0-9]|99[1-9]))[0-9]{1,3}\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)</match>
    <description>sshd: Authentication failed from a public IP address $(srcip).</description>
    <group>authentication_failed,authentication_success,pci_dss_10.2.4,pci_dss_10.2.5,</group>
  </rule>

  <rule id="100030" level="5">
    <if_sid>5715</if_sid>
    <match type="pcre2">\b(?!(10)|192\.168|172\.(2[0-9]|1[6-9]|3[0-1])|(25[6-9]|2[6-9][0-9]|[3-9][0-9][0-9]|99[1-9]))[0-9]{1,3}\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)</match>
    <description>sshd: Authentication succeeded from a public IP address $(srcip).</description>
    <group>authentication_failed,authentication_success,pci_dss_10.2.4,pci_dss_10.2.5,</group>
  </rule>

  <rule id="100004" level="10">
    <field name="abuseipdb.source.rule" type="pcre2">^100002$</field>
    <field name="abuseipdb.abuse_confidence_score" type="pcre2" negate="yes">^0$</field>
    <description>AbuseIPDB: SSH Authentication failed from a public IP address $(srcip) with $(abuseipdb.abuse_confidence_score)% confidence of abuse.</description>
    <group>authentication_failed,pci_dss_10.2.4,pci_dss_10.2.5,</group>
  </rule>

  <rule id="100005" level="14">
    <field name="abuseipdb.source.rule" type="pcre2">^100030$</field>
    <field name="abuseipdb.abuse_confidence_score" type="pcre2" negate="yes">^0$</field>
    <description>AbuseIPDB: SSH Authentication succeeded from a public IP address $(srcip) with $(abuseipdb.abuse_confidence_score)% confidence of abuse.</description>
    <group>authentication_failed,pci_dss_10.2.4,pci_dss_10.2.5,</group>
  </rule>
</group>
```

---

## ⚙️ Integration & Active Response

### Integration with AbuseIPDB:

```xml
<integration>
  <name>custom-abuseipdb.py</name>
  <api_key>YOURAPIKEY</api_key>
  <rule_id>100002,100030</rule_id>
  <alert_format>json</alert_format>
</integration>
```

### Active Response:

```xml
<command>
  <name>firewall-drop</name>
  <executable>firewalld-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>100004,100005,5503,5710,5712</rules_id>
</active-response>
```

Apply permissions:

```bash
# Download
wget https://raw.githubusercontent.com/jomocasec1990/wazuh-siem-lab/main/10-AbuseIPDB-Wazuh-ActiveResponse/AbuseIPDB-Script/custom-abuseipdb.py

# Set permissions
chmod 750 /var/ossec/integrations/custom-abuseipdb.py
chown root:wazuh /var/ossec/integrations/custom-abuseipdb.py
```

Restart Wazuh:

```bash
systemctl restart wazuh-manager
```

---

## 🥷 Attack Simulation

From Kali Linux (spoofed to TOR exit node `185.220.101.1`):

**Prepare a wordlist:**

```bash
echo -e "123456\nadmin\npassword\nletmein" > passwords.txt
```

**Run brute force attack:**

```bash
hydra -l jomoca -P passwords.txt ssh://45.65.189.83
```

**Expected Result:** IP should get blocked after multiple failures.

---

## 🔎 Wazuh Alert Output

Detected rules:

* `100002` - SSH failed login from public IP
* `100004` - AbuseIPDB confirms IP is malicious
* `5503` - PAM login failure (MITRE T1110.001)
* `651` - Active Response triggered (firewall-drop)

Sample alert:

```json
"rule": {
  "id": "651",
  "description": "Host Blocked by firewall-drop Active Response",
  "level": 3
},
"data": {
  "srcip": "185.220.101.1",
  "dstuser": "jomoca",
  "command": "add"
}
```

---

## 👁️ Confirm IP Block

```bash
sudo iptables -S | grep 185.220.101.1
```

---

## 📄 Related Rules Used

* **5503** - PAM login failed
* **5710** - Non-existent user
* **5712** - Brute force pattern
* **100002 / 100030** - Custom public IP match
* **100004 / 100005** - AbuseIPDB enrichment
* **651** - Active response triggered

---

## 🌟 Conclusion

This lab successfully demonstrates how to:

1. Detect SSH brute force attempts.
2. Enrich logs using AbuseIPDB.
3. Actively block malicious IPs using Wazuh's native `firewalld-drop` binary.
4. Monitor all steps in Kibana or Wazuh dashboard.
