import os
import csv
from dotenv import load_dotenv
from tabulate import tabulate
 
from scripts.subscribers_list import main as subscribers_main
from scripts.bng import get_bng_ip
from scripts.acs import get_acs_ip
from scripts.radius import connect_to_mysql, get_radius_ip_from_connection
 
load_dotenv()
 
def read_usernames(file_path):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return []
 
def main():
    # Appelle le sous-script s’il fait quelque chose d’important
    subscribers_main()
 
    usernames_file = os.getenv("USERNAMES_FILE")
    if not usernames_file:
        print("❌ USERNAMES_FILE not set in .env")
        return
 
    usernames = read_usernames(usernames_file)
    if not usernames:
        print("❌ No usernames loaded")
        return
 
    result = []
 
    connection = connect_to_mysql()
    if not connection:
        print("❌ Unable to connect to MySQL")
        return
 
    try:
        for user in usernames:
            ip_bng = get_bng_ip(user)
            ip_acs = get_acs_ip(user)
            ip_radius = get_radius_ip_from_connection(connection, user)
            result.append([user, ip_bng, ip_acs, ip_radius])
    finally:
        connection.close()
        print("\n🔚 MySQL connection closed")
 
    print()
    print(tabulate(result, headers=["Username", "IP BNG", "IP ACS", "IP Radius"], tablefmt="fancy_grid"))
 
    os.makedirs("output", exist_ok=True)
    with open("output/result.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Username", "IP BNG", "IP ACS", "IP Radius"])
        writer.writerows(result)
 
if __name__ == "__main__":
    main()
