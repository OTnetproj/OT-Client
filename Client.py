import os
import pyModbusTCP
from pyModbusTCP.client import ModbusClient
import random
import time


server1='132.72.48.12'
server2='132.72.48.14'
port=502

# Water Tank configuration
WATER_LEVEL_ADDR = 0    # input register address
HIGH_MARK_ADDR = 0      # discrete input/holding register sensor address for high water level 
LOW_MARK_ADDR = 1       # discrete input/holding register sensor address for low water level
WATER_PUMP_ADDR = 0     # coil address for turn on/off water pump at server
prev_water_level, prev_high_status, prev_low_status, pump_status

def print_server(water_level,high_status,low_status,pump_status):
    print(f"    Water level is: {water_level}")
    print(f"    High status is: {high_status}")
    print(f"    Low status is: {low_status}")
    print(f"    pump status is: {pump_status}")

client1 = ModbusClient(host=server1,port=port,unit_id=1)
client2 = ModbusClient(host=server2,port=port,unit_id=2)

if not client1.open():
    print("Unable to connect server")

else:
    print("Connected to server")

try:
    prev_water_level = client1.read_input_registers(WATER_LEVEL_ADDR,1)[0]
    prev_high_status = client1.read_discrete_inputs(HIGH_MARK_ADDR,1)[0]
    prev_low_status = client1.read_discrete_inputs(LOW_MARK_ADDR,1)[0]
    pump_status = client1.read_coils(WATER_PUMP_ADDR,1)[0]
    
    while True:
        current_water_level = client1.read_input_registers(WATER_LEVEL_ADDR,1)[0]
        current_high_status = client1.read_discrete_inputs(HIGH_MARK_ADDR,1)[0]
        current_low_status = client1.read_discrete_inputs(LOW_MARK_ADDR,1)[0]
        # turn off water pump
        if prev_water_level < current_water_level and current_water_level >= client1.read_holding_registers(HIGH_MARK_ADDR,1)[0]:
            if current_high_status == False:
                client1.write_single_coil(HIGH_MARK_ADDR,[1])

        # turn on water pump 
        if prev_water_level > current_water_level and current_water_level >= client1.read_holding_registers(LOW_MARK_ADDR,1)[0]:
            if current_low_status == False:
                client1.write_single_coil(LOW_MARK_ADDR,[0])
        
        prev_water_level = current_water_level
        prev_high_status = current_high_status
        prev_low_status = current_low_status
        print_server(current_water_level,current_high_status,current_low_status,pump_status)
        time.sleep(1)

except KeyboardInterrupt:
    print("Client is stopping...")
    client1.close()
    print("Client is closed")

