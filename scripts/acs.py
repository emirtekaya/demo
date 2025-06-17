import os
import json
import urllib.parse
import requests
from dotenv import load_dotenv


def get_acs_ip(username):
    ACS_BASE_URL = os.getenv("ACS_BASE_URL", "http://13.69.26.119:7557/devices")  # fallback default
    field = "VirtualParameters.PPPoEUsername"
    query = urllib.parse.quote(json.dumps({field: username}))
 
    try:
        response = requests.get(f"{ACS_BASE_URL}/?query={query}")
        response.raise_for_status()
        device_list = response.json()
 
        if not device_list:
            return "N/A"
 
        device_id = device_list[0]["_id"]
 
        projection = urllib.parse.quote(",".join([
            "Device.PPP.Interface.2.IPCP.LocalIPAddress",
            "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANPPPConnection.1.ExternalIPAddress"
        ]))
 
        query_id = urllib.parse.quote(json.dumps({"_id": device_id}))
        full_url = f"{ACS_BASE_URL}?query={query_id}&projection={projection}"
 
        r = requests.get(full_url)
        r.raise_for_status()
        data = r.json()
 
        if not data:
            return "N/A"
 
        val = data[0]
        for part in "Device.PPP.Interface.2.IPCP.LocalIPAddress".split("."):
            val = val.get(part, {})
 
        return val.get("_value", "N/A")
 
    except Exception as e:
        print(f"[ACS Error for {username}] {e}")
        return "N/A"
