#!/usr/bin/python3

# Imports the Google Cloud client library
import logging
import time
import requests
import socket
import google.cloud.logging

# ------------------
# Setup Logging
# ------------------

auth_file = '/home/pi/host_info_logger/keys/homelab-266121-2389cbbb58c3.json'
client = google.cloud.logging.Client.from_service_account_json(auth_file)
client.setup_logging()


# ------------------
# Run Script
# ------------------

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return(IP)

ip_address_public_backup = ""
hostname_backup = ""
ip_address_local_backup = ""
info_changed = 0
run_count = 0

while True:    
    # Get Host Info
    try:
        ip_address_public = requests.get("https://api.myip.com").json()['ip']
    except:
        ip_address_public = ""
    try:
        hostname = socket.gethostname()
    except:
        hostname = ""
    try:
        ip_address_local = get_ip()
    except:
        ip_address_local = ""

    # Check to see if anything has changed since the last run
    if ip_address_public != ip_address_public_backup:
        info_changed = 1
    if hostname != hostname_backup:
        info_changed = 1
    if ip_address_local != ip_address_local_backup:
        info_changed = 1

    # If anything has changed then send a log and update the backup    
    if info_changed == 1:
        print("Logging changes")
        logging.log(msg="{{Hostname:{}, Global_IP_Address:{}, Local_IP_Address:{}}}".format(hostname, ip_address_public, ip_address_local), level=logging.INFO)
        ip_address_public_backup = ip_address_public
        hostname_backup = hostname
        ip_address_local_backup = ip_address_local
        info_changed = 0
    elif run_count == 10:
        print("Logging keepalive")
        logging.log(msg="{{Hostname:{}, Global_IP_Address:{}, Local_IP_Address:{}}}".format(hostname, ip_address_public, ip_address_local), level=logging.INFO)
        ip_address_public_backup = ip_address_public
        hostname_backup = hostname
        ip_address_local_backup = ip_address_local
        run_count = 0
    else:
        print("No changes to log")
    run_count += 1
    time.sleep(30)
