import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

server_ip = os.getenv("BNG_SERVER_IP")
auth_user = os.getenv("BNG_USER")
auth_pass = os.getenv("BNG_PASS")
output_file = os.getenv("USERNAMES_FILE")

if not server_ip or not auth_user or not auth_pass or not output_file:
    print("❌ One or more environment variables are missing.")
    exit(1)

curl_command = [
    "curl",
    f"http://{server_ip}:2000/rpc/get-subscribers/extensive",
    "-u", f"{auth_user}:{auth_pass}",
    "-H", "Content-Type: application/xml",
    "-H", "Accept: application/json"
]

def main():
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            print("❌ Curl failed:")
            print(result.stderr)
            return

        output = result.stdout.strip()

        if not output:
            print("❌ Curl returned empty output.")
            return

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            print("❌ Failed to decode JSON. Here is the raw output:")
            print(output)
            return

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print("❌ Nested JSON decoding failed.")
                return

        subscribers_info = data.get("subscribers-information")
        if not subscribers_info:
            print("❌ 'subscribers-information' not found in the response.")
            return

        subscribers = subscribers_info[0].get("subscriber", [])
        usernames = []

        for sub in subscribers:
            user_name_list = sub.get("user-name", [])
            if user_name_list and isinstance(user_name_list[0], dict):
                username = user_name_list[0].get("data")
                if username:
                    usernames.append(username)

        # Assure que le dossier de sortie existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Écrit les usernames dans le fichier
        with open(output_file, "w") as file:
            file.write("\n".join(usernames))

        print(f"✅ {len(usernames)} usernames saved to {output_file}")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
