import os, sys
from IPython.display import display
import pandas as pd
import traci
import categorise as c
import statespace as state


stateSpace = state.StateSpace("C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui")

# Running Sumo
sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo','tools'))
sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"

# File to run
sumoCmd = [sumoBinary, "-c", "_sumo\\simplest_intersection.sumocfg"]

# used to set the display to automatic
pd.options.display.width = 0

traci.start(sumoCmd) # Need to press play in the GUI after this

categoriser = c.Category()

for _ in range(1000):

    traci.simulationStep()

    vehicles_df = pd.DataFrame()
    horizontal = pd.DataFrame()
    vertical = pd.DataFrame()

    # Get vehicle count
    traci.vehicle.getIDCount()

    vehicle_ids = list(traci.vehicle.getIDList())
    arrivedVehicles = list(traci.simulation.getArrivedIDList())

    # remove the arrived vehicles
    for arrived in arrivedVehicles:
        if arrived in vehicle_ids:
            vehicle_ids.remove(arrived)

    # get the vehicle id's that have moved beyond the detector range and remove them from the list
    for detected in traci.multientryexit.getLastStepVehicleIDs('intersection_detector'):
        if detected in vehicle_ids:
            vehicle_ids.remove(detected)



    for vehicle_id in vehicle_ids:

        stopped_state = traci.vehicle.getStopState(vehID=vehicle_id) # I don't think stopped state means what we thought
        waiting_time = traci.vehicle.getWaitingTime(vehID=vehicle_id)
        accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehID=vehicle_id)
        speed = traci.vehicle.getSpeed(vehID=vehicle_id)


        newVehicle = pd.DataFrame(
                        {
                            'vehicle_id' : [vehicle_id],
                            'waiting_time': [waiting_time],
                            'accumulated_waiting_time': [accumulated_waiting_time],
                            'stopped_state': [stopped_state],
                            'speed': [speed]
                        }
        )

        # if our list of vehicles is not empty
        if not vehicles_df.empty:

            # check if the vehicle already exists
            index = vehicles_df.index
            condition = vehicles_df['vehicle_id'] == vehicle_id
            existingIndex = index[condition]
            indexList = existingIndex.to_list()
            #existingIndex = vehicles_df.index[vehicles_df['vehicle_id'] == vehicle_id].tolist()

            if len(indexList) > 0:
                vehicles_df.iloc[indexList[0]] = newVehicle.iloc[0]
                continue

        # if the dataframe is empty or does not contain the new vehicle id then insert the new vehicle
        vehicles_df = pd.concat([vehicles_df, newVehicle], ignore_index=True)

    # get the vehicle state space
    horizontal, vertical, hTime, vTime = categoriser.categorise(vehicles_df)

    # get the traffic light state space
    idList = traci.trafficlight.getIDList()
    trafficLightCount = traci.trafficlight.getIDCount()
    lightStateString = traci.trafficlight.getRedYellowGreenState('intersection')

    lightState = categoriser.convertLightStateToInt(lightStateString)

    #display(lightState)


traci.close()