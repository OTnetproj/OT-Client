import os
import psutil
import json
import time
import datetime
import requests
import logging
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

elk_pass = os.getenv('ELASTIC_PASSWORD')
url = "https://132.72.48.18:9200/clients/_doc?pipeline=add_date"
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# define info and error logs for post requests
logging.basicConfig(level=logging.INFO, filename="/var/log/OT/clients.log", filemode="w", format='%(asctime)s - %(levelname)s - %(message)s')

def monitor(prev):
	current = set()
	for conn in psutil.net_connections():
		if conn.laddr.port == 502 and conn.status == 'ESTABLISHED':
			current.add((conn.raddr.ip,conn.raddr.port))
	new_clients = current - prev
	to_remove_clients = prev - current
	current_details=[{"IP": ip, "Port": port} for ip, port in current]
	current_clients_json = {
		"message_type": "repetetive_check",
		"clients_count": len(current),
		"Clients_details": current_details,
		"timestamp": datetime.datetime.now().isoformat()
	}
	if(len(new_clients)):
		new_clients_add(new_clients)
	if(len(to_remove_clients)):
		old_clients_removal(to_remove_clients)
	post_to_elastic(current_clients_json)
	return list(current)

def new_clients_add(new):
	new_details=[{"IP": ip, "Port": port} for ip, port in new]
	new_clients_json = {
		"message_type": "new_clients_added",
		"clients_count_diff": len(new),
		"clients_details_diff": new_details,
		"timestamp": datetime.datetime.now().isoformat()
	}
	post_to_elastic(new_clients_json)


def old_clients_removal(old):
	old_details=[{"IP": ip, "Port": port} for ip, port in old]
	old_clients_json = {
		"message_type": "client_disconnected",
		"clients_count_diff": len(old),
		"clients_details_diff": old_details,
		"timestamp": datetime.datetime.now().isoformat()
	}
	post_to_elastic(old_clients_json)

def post_to_elastic(payload):
	response = requests.post(
		url,
		auth=HTTPBasicAuth('elastic', elk_pass),
		headers={'Content-Type': 'application/json'},
		json=payload,
		verify=False
	)
	if response.status_code not in [200,201]:
		logging.error(f"Error: Received status code {response.status_code}")
	else:
		logging.info(f"Info: Received status code {response.status_code}")


def main():
	current_clients = set()
	for conn in psutil.net_connections():
		if conn.laddr.port == 502 and conn.status == 'ESTABLISHED':
			current_clients.add((conn.raddr.ip,conn.raddr.port))
	while True:
		time.sleep(10)
		update = monitor(current_clients)
		current_clients.clear()
		current_clients.update(update)


if __name__ == "__main__":
	main()
