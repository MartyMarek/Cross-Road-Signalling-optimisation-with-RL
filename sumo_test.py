import os, sys
import pandas as pd

# if 'SUMO_HOME' in os.environ:
#     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#     sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

# Running Sumo
sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo','tools'))
#sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"
sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo"

# File to run
sumoCmd = [sumoBinary, "-c", "_sumo\\simplest_intersection.sumocfg"]

import traci
traci.start(sumoCmd) # Need to press play in the GUI after this
traci.simulation.start()
traci.simulationStep()
traci.simulation.getEndTime()
traci.simulation.getTime()
traci.multientryexit.getIDList() # Get detector ID
traci.simulationStep()
traci.multientryexit.getLastStepVehicleIDs(detID='intersection_detector') # Get the vehicles currently in the intersection
traci.simulation.getArrivedIDList()
traci
for i in range(0,100000):
    traci.simulationStep()
    traci.multientryexit.getLastStepVehicleIDs(detID='intersection_detector') 


# Get all vehicles
traci.vehicle.getIDList()
# Get vehicle count
traci.vehicle.getIDCount()
import numpy as np
np.inf
vehicle_ids = traci.vehicle.getIDList()

vehicles_df = pd.DataFrame()

for vehicle_id in vehicle_ids:
    
    stopped_state = traci.vehicle.getStopState(vehID=vehicle_id) # I don't think stopped state means what we thought
    waiting_time = traci.vehicle.getWaitingTime(vehID=vehicle_id)
    accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehID=vehicle_id)
    speed = traci.vehicle.getSpeed(vehID=vehicle_id)

    vehicle_df = pd.DataFrame(
        data=
        [[
            vehicle_id,
            waiting_time,
            accumulated_waiting_time,
            stopped_state,
            speed
        ]],
        columns=
        [
            "vehicle_id",
            "waiting_time",
            "accumulated_waiting_time",
            "stopped_state",
            "speed"
        ]
    )

    vehicles_df = pd.concat(
        [
            vehicles_df,
            vehicle_df
        ],
        ignore_index=True
    )
    

vehicles_df

traci.simulationStep()
step = 0
print("A")


while step < 1000:
   traci.simulationStep()
   
   step += 1


traci.simulation.isLoaded()

traci.close()

