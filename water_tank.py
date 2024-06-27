import pyModbusTCP
from pyModbusTCP.server import ModbusServer, DataBank
import os
import random
import time

# Server host and port prameters
host='132.72.48.20'
port=502

# Server Data Bank
serv_DB = DataBank(coils_size=1,d_inputs_size=2,h_regs_size=2,i_regs_size=2)

# Server define coils, discrete inputs and registers
WATER_PUMP_ADDR = 0         # coil address for water pump state 
WATER_LEVEL_ADDR = 0        # input register address for water level
HIGH_MARK_ADDR = 0          # discrete input address for high water mark sensor
LOW_MARK_ADDR = 1           # discrete input address for low water mark sensor
HIGH_LEVEL_THRESHOLD = 17   # hold register value for water tank overflow 17/20
LOW_LEVEL_THRESHOLD = 3     # hold register value for water tank near-empty tank 3/20
OPTIMAL_LEVEL = 10          # retore water tank level value when exceeding threshold

def server_init(serv_DB,host,port):
    # initialize server's coils, input and registers to water tank
    serv_DB.set_input_registers(WATER_LEVEL_ADDR, [OPTIMAL_LEVEL])
    serv_DB.set_holding_registers(HIGH_MARK_ADDR, [17])
    serv_DB.set_holding_registers(LOW_MARK_ADDR, [3])
    serv_DB.set_discrete_inputs(HIGH_MARK_ADDR, [0])
    serv_DB.set_discrete_inputs(LOW_MARK_ADDR, [0])
    server = ModbusServer(host=host,port=port,no_block=True,data_bank=serv_DB)
    return server

def update_water_tank(server,serv_DB):
    rand_shift = random.choice([0,1]) # randomly increase / decrease water tank by on level
    current_water_level = serv_DB.get_input_registers(WATER_LEVEL_ADDR,1)[0]
    if serv_DB.get_coils(WATER_PUMP_ADDR,1)[0] == 1: # pump is on
        serv_DB.set_input_registers(WATER_LEVEL_ADDR, [current_water_level+rand_shift])
    else: # pump is off
        serv_DB.set_input_registers(WATER_LEVEL_ADDR, [current_water_level-rand_shift])
        
def run_server(server,serv_DB):
    current_water_level = serv_DB.get_input_registers(WATER_LEVEL_ADDR,1)[0]
    if current_water_level >= serv_DB.get_holding_registers(HIGH_MARK_ADDR,1)[0]:
        serv_DB.set_discrete_inputs(HIGH_MARK_ADDR,[1])
    if current_water_level <= serv_DB.get_holding_registers(LOW_MARK_ADDR,1)[0]:
        serv_DB.set_discrete_inputs(LOW_MARK_ADDR,[1])
    else:
        serv_DB.set_discrete_inputs(HIGH_MARK_ADDR,[0,0])

def print_tank_status(server,serv_DB):
    current_level = serv_DB.get_input_registers(WATER_LEVEL_ADDR,1)[0]
    water_pump_status = serv_DB.get_coils(0,1)[0]
    print("Water Tank Stats:")
    print(f"    Water tank current level: {current_level} cm")
    print(f"    Water pump statusis : {water_pump_status}")



# Modbus Server object 
server = server_init(serv_DB,host,port)
server.start()
print("server start")

try:
    while True:
        run_server(server,serv_DB)
        update_water_tank(server,serv_DB)
        print_tank_status(server,serv_DB)
        time.sleep(3)
except KeyboardInterrupt:
    print("Server is stopping...")
    server.stop()
    print("Server stopped")


