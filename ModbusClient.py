import os
import pyModbusTCP
from pyModbusTCP.client import ModbusClient
import time
import random
import threading

# init clients from outside list and remote registers define
file_path='ModbusServers.txt'
WATER_LEVEL_ADDR = 0        # input register address for tank's water level
HIGH_MARK_ADDR = 0          # discrete input and holding register addresses for HIGH mark state and threshold value 
LOW_MARK_ADDR = 1           # discrete input and holding register addresses for LOW mark state and threshold value
WATER_PUMP_ADDR = 0         # Coils address for water tank's pump status

class Session(threading.Thread):
    def __init__(self,server_ip,server_port,unit_id):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.unit_id = unit_id
        self.client = ModbusClient(host=server_ip,port=server_port,unit_id=unit_id)

    def run(self):
        if not self.client.open():
            print(f"    Failed to open session with server: {self.server_ip}")
            return
        else:
            print(f"    Connected to server: {self.server_ip}")

        try:
            while True:
                # Read Water level
                water_level = self.client.read_input_registers(WATER_LEVEL_ADDR,1)[0]
                if water_level:
                    print(f"{self.server_ip} Current water level is: {water_level}")
                    high_mark_state = self.client.read_discrete_inputs(HIGH_MARK_ADDR,1)[0]
                    low_mark_state = self.client.read_discrete_inputs(LOW_MARK_ADDR,1)[0]
                    pump_state = self.client.read_coils(WATER_PUMP_ADDR,1)[0]

                    # turn on water pump 
                    if not pump_state and low_mark_state:
                        self.client.write_single_coil(WATER_PUMP_ADDR,1)
                        print(f"{self.server_ip} water pump turned on")
                    #turn off water pump
                    elif pump_state and high_mark_state:
                        self.client.write_single_coil(WATER_PUMP_ADDR,0)
                        print(f"{self.server_ip} water pump turned off")
                time.sleep(1)

        except KeyboardInterrupt:
            print(f"Session for server {self.server_ip} is stopping")
        finally:
            self.client.close()
            print(f"Disconnected from server: {self.server_ip}")

def start_modbus_client(file_path):
    servers_list = []
    f = open(file_path,"r")
    for line in f:
        parts = line.split()
        if len(parts) == 2:
            servers_list.append(parts[1])
    print(servers_list)
    sessions = [Session(ip,502,1) for ip in servers_list]
    for session in sessions:
        session.start()

    for session in sessions:
        session.join()

if __name__ == "__main__":
    start_modbus_client(file_path)





