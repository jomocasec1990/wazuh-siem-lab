import json
import sys
import time
import os
from socket import socket, AF_UNIX, SOCK_DGRAM

try:
    import requests
except Exception as e:
    print("No module 'requests' found. Install: pip install requests")
    sys.exit(1)

# Global vars
debug_enabled = False
pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
now = time.strftime("%a %b %d %H:%M:%S %Z %Y")
log_file = '{0}/logs/integrations.log'.format(pwd)
socket_addr = '{0}/queue/sockets/queue'.format(pwd)

def main(args):
    debug("# Starting")
    alert_file_location = args[1]
    apikey = args[2]

    debug("# API Key: {}".format(apikey))
    debug("# File location: {}".format(alert_file_location))

    with open(alert_file_location) as alert_file:
        json_alert = json.load(alert_file)

    debug("# Processing alert: {}".format(json_alert))

    msg = request_abuseipdb_info(json_alert, apikey)

    if msg:
        send_event(msg, json_alert["agent"])

def debug(msg):
    if debug_enabled:
        msg = "{0}: {1}\n".format(now, msg)
        print(msg)
        with open(log_file, "a") as f:
            f.write(msg)

def collect(data):
    return (
        data.get('abuseConfidenceScore'),
        data.get('countryCode'),
        data.get('usageType'),
        data.get('isp'),
        data.get('domain'),
        data.get('totalReports'),
        data.get('lastReportedAt')
    )

def in_database(data, srcip):
    return data.get('totalReports', 0) > 0

def query_api(srcip, apikey):
    params = {'maxAgeInDays': '90', 'ipAddress': srcip}
    headers = {
        "Accept-Encoding": "gzip, deflate",
        'Accept': 'application/json',
        "Key": apikey
    }
    response = requests.get('https://api.abuseipdb.com/api/v2/check', params=params, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", {})
    else:
        alert_output = {
            "abuseipdb": {
                "error": response.status_code,
                "description": response.json().get("errors", [{}])[0].get("detail", "Unknown error")
            },
            "integration": "custom-abuseipdb"
        }
        debug("# Error: {}".format(alert_output["abuseipdb"]))
        send_event(alert_output)
        exit(0)

def request_abuseipdb_info(alert, apikey):
    if "srcip" not in alert.get("data", {}):
        return 0

    srcip = alert["data"]["srcip"]
    data = query_api(srcip, apikey)

    alert_output = {
        "abuseipdb": {
            "found": 0,
            "source": {
                "alert_id": alert.get("id"),
                "rule": alert["rule"]["id"],
                "description": alert["rule"]["description"],
                "full_log": alert.get("full_log", ""),
                "srcip": srcip
            }
        },
        "abuseipdb.source.rule": alert["rule"]["id"],
        "integration": "custom-abuseipdb"
    }

    if in_database(data, srcip):
        alert_output["abuseipdb"]["found"] = 1
        (
            abuse_confidence_score,
            country_code,
            usage_type,
            isp,
            domain,
            total_reports,
            last_reported_at
        ) = collect(data)

        alert_output["abuseipdb"].update({
            "abuse_confidence_score": abuse_confidence_score,
            "country_code": country_code,
            "usage_type": usage_type,
            "isp": isp,
            "domain": domain,
            "total_reports": total_reports,
            "last_reported_at": last_reported_at
        })

    debug(alert_output)
    return alert_output

def send_event(msg, agent=None):
    if not agent or agent.get("id") == "000":
        string = '1:abuseipdb:{0}'.format(json.dumps(msg))
    else:
        string = '1:[{0}] ({1}) {2}->abuseipdb:{3}'.format(
            agent["id"],
            agent["name"],
            agent.get("ip", "any"),
            json.dumps(msg)
        )

    debug("# Sending event to Wazuh: {}".format(string))
    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect(socket_addr)
    sock.send(string.encode())
    sock.close()

if __name__ == "__main__":
    try:
        if len(sys.argv) >= 3:
            if len(sys.argv) > 3 and sys.argv[3] == 'debug':
                debug_enabled = True
            main(sys.argv)
        else:
            debug("# Exiting: Bad arguments.")
            sys.exit(1)
    except Exception as e:
        debug(str(e))
        raise
