import os, sys
import pandas as pd
import xml.etree.ElementTree as ET

from pyparsing import col

# if 'SUMO_HOME' in os.environ:
#     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#     sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

traffic = tree = ET.parse('C:\\sumoconfig\\real_intersection_traffic.rou.xml')
root = traffic.getroot()
children = list(root)

routes = list()

for child in children:
    if 'flow' in child.attrib['id']:
        routes.append(child.attrib['id'].replace("flow_",""))

routes

frame = pd.DataFrame(
    columns=[
        'approaching_cars',
        'stopped_cars',
        'average_speed',
        'accumulated_waiting_time',
        'new_throughput'
    ],
    index=routes
).fillna(0).sort_index()
frame.index.name = 'routes'
frame
# Running Sumo
sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo','tools'))
sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"
#sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo"

# File to run
sumoCmd = [sumoBinary, "-c", "C:\\sumoconfig\\real_intersection.sumocfg"]


import traci
traci.start(sumoCmd) # Need to press play in the GUI after this

traci.trafficlight.getCompleteRedYellowGreenDefinition(tlsID='intersection')
traci.trafficlight.getCompleteRedYellowGreenDefinition(tlsID='intersection')
traci.trafficlight.getRedYellowGreenState(tlsID='intersection')
traci.trafficlight.setRedYellowGreenState(tlsID='intersection',state='GGrrGGrr')
traci.trafficlight.setRedYellowGreenState(tlsID='intersection',state='rrGGrrGG')
traci.trafficlight.setRedYellowGreenState(tlsID='intersection',state='rrrrrrrrrr')




routes

len(lista)

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


    first_frame = False

    if vehicle_id not in list(vehicles_state.index.unique()):
        first_frame = True

    if speed < 0.5 and not first_frame:
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
            'first_frame': [first_frame]
        },
        index=[vehicle_id]
    )

    vehicles_state = pd.concat([vehicles_state[~vehicles_state.index.isin(vehicle_state.index)], vehicle_state])
    vehicles_state.update(vehicle_state)


def collapseSimStateToObs(x):

    output_dict = dict()
    output_dict['approaching_cars'] = x.loc[x['status'] == 'Approaching_Interection'].index.nunique()
    output_dict['stopped_cars'] = x.loc[
        (x['status'] == 'Approaching_Interection') & 
        (x['stopped'] == True)
    ].index.nunique()
    output_dict['average_speed'] = x.loc[
        ((x['status'] == 'Approaching_Interection') |
        (x['status'] == 'In_Interection')) &
        (x['first_frame'] == False),
        'speed'
    ].mean()
    output_dict['accumulated_waiting_time'] = x.loc[x['status'] == 'Approaching_Interection','accumulated_waiting_time'].sum()
    output_dict['new_throughput'] = x.loc[x['new_throughput'] == True].index.nunique()

    return pd.Series(data=output_dict)

routes = set()

for item in traci.route.getIDList():
    routes.add(item.split(".")[0].replace("!","").replace("flow_",""))

empty_observations = pd.DataFrame(
    columns=[
        'approaching_cars',
        'stopped_cars',
        'average_speed',
        'accumulated_waiting_time',
        'new_throughput'
    ],
    index=routes
).fillna(0).sort_index()
empty_observations.index.name = 'routes'

current_observations = vehicles_state.groupby('route').apply(lambda x: collapseSimStateToObs(x=x))
empty_observations.update(current_observations)
empty_observations.values.flatten().shape

current_observations
vehicles_state



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

