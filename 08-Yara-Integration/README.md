
# Wazuh YARA Integration on Windows (Active Response)

This lab demonstrates how to integrate YARA into the Wazuh agent on Windows to automatically scan files detected by Syscheck (file integrity monitoring). When a new or modified file is found in a specific directory (e.g. Downloads), Wazuh triggers an Active Response, executes a custom yara.bat script, and logs the scan result, which is then analyzed using a custom decoder and rule.

## :hammer_and_wrench: Step-by-Step Setup

### 1. Download and Install YARA for Windows
```powershell
Invoke-WebRequest -Uri https://github.com/VirusTotal/yara/releases/download/v4.5.2/yara-v4.5.2-2326-win64.zip -OutFile v4.5.2-2326-win64.zip
Expand-Archive v4.5.2-2326-win64.zip; Remove-Item v4.5.2-2326-win64.zip
```
[Official release page](https://github.com/VirusTotal/yara/releases/)

### 2. Move YARA binary to the Wazuh agent
```powershell
mkdir 'C:\Program Files (x86)\ossec-agent\active-response\bin\yara\'
cp .\v4.5.2-2326-win64\yara64.exe 'C:\Program Files (x86)\ossec-agent\active-response\bin\yara\'
```

### 3. Install Valhalla API to fetch rules
```powershell
pip install valhallaAPI
mkdir 'C:\Program Files (x86)\ossec-agent\active-response\bin\yara\rules'
cd 'C:\Program Files (x86)\ossec-agent\active-response\bin\yara\rules'
Invoke-WebRequest -Uri https://raw.githubusercontent.com/Mazuco/wazuh/refs/heads/main/download_yara_rules.py -OutFile download_yara_rules.py
```

### 4. Python script to download YARA rules
```python
from valhallaAPI.valhalla import ValhallaAPI
v = ValhallaAPI(api_key="1111111111111111111111111111111111111111111111111111111111111111")
response = v.get_rules_text()
with open('yara_rules.yar', 'w') as fh:
    fh.write(response)
```
Then:
```powershell
cd 'C:\Program Files (x86)\ossec-agent\active-response\bin\yara\rules'
python.exe .\download_yara_rules.py
```

### 5. Create the YARA execution script (yara.bat)

**C:\Program Files (x86)\ossec-agent\active-response\bin\yara.bat**
```bat
@echo off
setlocal enableDelayedExpansion

reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && SET OS=32BIT || SET OS=64BIT

if %OS%==32BIT (
    SET log_file_path="%programfiles%\ossec-agent\active-response\active-responses.log"
)
if %OS%==64BIT (
    SET log_file_path="%programfiles(x86)%\ossec-agent\active-response\active-responses.log"
)

set input=
for /f "delims=" %%a in ('PowerShell -command "$logInput = Read-Host; Write-Output $logInput"') do (
    set input=%%a
)

set json_file_path="C:\Program Files (x86)\ossec-agent\active-response\stdin.txt"
echo %input% > %json_file_path%

for /F "tokens=* USEBACKQ" %%F in (`Powershell -Nop -C "(Get-Content '%json_file_path%'|ConvertFrom-Json).parameters.alert.syscheck.path"`) do (
    set syscheck_file_path=%%F
)

del /f %json_file_path%

set yara_exe_path="C:\Program Files (x86)\ossec-agent\active-response\bin\yara\yara64.exe"
set yara_rules_path="C:\Program Files (x86)\ossec-agent\active-response\bin\yara\rules\yara_rules.yar"

for /f "delims=" %%a in ('powershell -command "& \"%yara_exe_path%\" \"%yara_rules_path%\" \"%syscheck_file_path%\" "') do (
    echo wazuh-yara: INFO - Scan result: %%a >> %log_file_path%
)
exit /b
```

## :gear: Wazuh Configuration (Manager Side)

### 6. Configure the decoder
File: `/var/ossec/etc/decoders/local_decoder.xml`
```xml
<decoder name="yara_decoder">
    <prematch>wazuh-yara:</prematch>
</decoder>
<decoder name="yara_decoder1">
    <parent>yara_decoder</parent>
    <regex>wazuh-yara: (\S+) - Scan result: (\S+) (\S+)</regex>
    <order>log_type, yara_rule, yara_scanned_file</order>
</decoder>
```

### 7. Create rules to trigger active response
File: `/var/ossec/etc/rules/local_rules.xml`
```xml
<group name="syscheck,">
  <rule id="100303" level="7">
    <if_sid>550</if_sid>
    <field name="file">C:\\Users\\Administrator\\Downloads</field>
    <description>File modified in C:\Users\Administrator\Downloads directory.</description>
  </rule>
  <rule id="100304" level="7">
    <if_sid>554</if_sid>
    <field name="file">C:\\Users\\Administrator\\Downloads</field>
    <description>File added to C:\Users\Administrator\Downloads directory.</description>
  </rule>
</group>

<group name="yara,">
  <rule id="108000" level="0">
    <decoded_as>yara_decoder</decoded_as>
    <description>Yara grouping rule</description>
  </rule>
  <rule id="108001" level="12">
    <if_sid>108000</if_sid>
    <match>wazuh-yara: INFO - Scan result: </match>
    <description>File "$(yara_scanned_file)" is a positive match. Yara rule: $(yara_rule)</description>
  </rule>
</group>
```

### 8. Configure Active Response
File: `/var/ossec/etc/ossec.conf`
```xml
<command>
  <name>yara_windows</name>
  <executable>yara.bat</executable>
  <timeout_allowed>no</timeout_allowed>
</command>

<active-response>
  <command>yara_windows</command>
  <location>local</location>
  <rules_id>100303,100304</rules_id>
</active-response>
```
Then restart Wazuh Manager:
```bash
sudo systemctl restart wazuh-manager
```

## :test_tube: Test the Setup

### 9. Trigger a YARA scan with EICAR file
```powershell
Invoke-WebRequest -Uri https://secure.eicar.org/eicar_com.zip -OutFile eicar.zip
Expand-Archive .\eicar.zip
cp .\eicar\eicar.com C:\Users\Administrator\Downloads
```

### 10. Verify detection in Wazuh Kibana
Look for logs like:
```
location: logs\yara_scan.log
full_log: wazuh-yara: INFO - Scan result: SUSP_Just_EICAR_RID2C24 c:\users\administrator\downloads\eicar\eicar.com
rule.id: 108001
rule.description: File "c:\users\administrator\downloads\eicar\eicar.com" is a positive match. Yara rule: SUSP_Just_EICAR_RID2C24

![Yara-Capture](Screenshots/wazuh-01-yara.png)
```

## :bookmark_tabs: Summary
This lab simulates a basic threat detection and response workflow using:
- YARA (for static file matching)
- Wazuh Syscheck (FIM)
- Wazuh Active Response
- Custom decoders/rules


