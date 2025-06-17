import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


def get_bng_ip(username):
    try:
        base_url = f"http://{os.getenv('BNG_SERVER_IP')}:2000"
        auth = HTTPBasicAuth(os.getenv("BNG_USER"), os.getenv("BNG_PASS"))
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/json"
        }

        response = requests.get(f"{base_url}/rpc/get-subscribers/extensive", headers=headers, auth=auth, timeout=60)
        response.raise_for_status()
        subs = response.json()
        subscribers = subs["subscribers-information"][0]["subscriber"]

        for s in subscribers:
            user = s.get("user-name", [{}])[0].get("data", "").lower()
            if user == username.lower():
                iface = s.get("interface", [{}])[0].get("data", "")
                if iface.startswith("pp0.") and s.get("access-type", [{}])[0].get("data", "") == "PPPoE":
                    resp = requests.get(f"{base_url}/rpc/get-ppp-interface-information/interface-name={iface}/extensive",
                                        headers=headers, auth=auth)
                    data = resp.json()
                    sessions = data.get("ppp-interface-information", [])[0].get("ppp-session", [])
                    for sess in sessions:
                        for section in sess.get("ppp-session-protocol-information", []):
                            if section.get("ppp-protocol", [{}])[0].get("data") == "IPCP":
                                ip = section.get("ppp-negotiated-options", [{}])[0].get("ipcp-address", [{}])[0].get("remote-address", [{}])[0].get("data", "N/A")
                                return ip
        return "N/A"
    except Exception:
        return "N/A"

