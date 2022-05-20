import os, sys
import pandas as pd

# if 'SUMO_HOME' in os.environ:
#     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#     sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

# Running Sumo
sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo','tools'))
sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"
#sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo"

# File to run
sumoCmd = [sumoBinary, "-c", "_sumo\\_config\\simplest_intersection.sumocfg"]


import traci
traci.start(sumoCmd) # Need to press play in the GUI after this


traci.simulationStep()
# Passed intersection

# Create set of vehicles that have passed the intersection
vehicles_state = pd.DataFrame()

vehicles_passed_intersection = set()
traci.simulationStep()

# Get vehicles that have passed
in_intersection_ids = traci.multientryexit.getLastStepVehicleIDs('intersection_detector')
vehicle_ids = traci.vehicle.getIDList()

for vehicle_id in vehicle_ids:

    waiting_time = traci.vehicle.getWaitingTime(vehID=vehicle_id)
    accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehID=vehicle_id)
    speed = traci.vehicle.getSpeed(vehID=vehicle_id)
    route = vehicle_id.split(".")[0].replace("flow_","")

    if speed == 0:
        stopped = True
    else:
        stopped = False

    status = None
    new_throughput = False

    if vehicle_id in in_intersection_ids and vehicle_id not in vehicles_passed_intersection:
        print("In intersection. New throughput.")
        vehicles_passed_intersection.add(vehicle_id)
        status = 'In_Interection'
        new_throughput = True
    elif vehicle_id in in_intersection_ids and vehicle_id in vehicles_passed_intersection:
        print("In intersection. Already counted.")
        status = 'In_Interection'
    elif vehicle_id not in in_intersection_ids and vehicle_id in vehicles_passed_intersection:
        print("Departed intersection. Already counted.")
        status = 'Departed_Intersection'
    elif vehicle_id not in in_intersection_ids and vehicle_id not in vehicles_passed_intersection:
        print("Approaching intersection.")
        status = 'Approaching_Interection'


    vehicle_state = pd.DataFrame(
        {
            #'vehicle_id': [vehicle_id],
            'route': [route],
            'speed': [speed],
            'stopped': [stopped],
            'status': [status],
            'new_throughput': [new_throughput],
            'waiting_time': [waiting_time],
            'accumulated_waiting_time': [accumulated_waiting_time],
        },
        index=[vehicle_id]
    )

    vehicles_state = pd.concat([vehicles_state[~vehicles_state.index.isin(vehicle_state.index)], vehicle_state])
    vehicle_state.update(vehicle_state)
vehicles_state

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

