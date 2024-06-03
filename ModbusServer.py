from pyModbusTCP.server import ModbusServer
import csv
from datetime import datetime
import code
import threading
import argparse

parser = argparse.ArgumentParser(description='Start Modbus server using port to your choice, default is 502')
parser.add_argument('--port', type=int, default=502)
args = parser.parse_args()

server = ModbusServer('132.72.48.20',args.port,no_block=True)

def start_server(server):
	try:
		print("Server is up")
		server.start()
	except:
		print("Server stopped")
		server.stop()


server_thread = threading.Thread(target=start_server(server))
server_thread.daemon = True
server_thread.start()

while True:
	pass

