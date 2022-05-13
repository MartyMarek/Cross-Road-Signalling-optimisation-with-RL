import os, sys
from IPython.display import display
import pandas as pd
import traci


# Running Sumo
sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo','tools'))
sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"

# File to run
sumoCmd = [sumoBinary, "-c", "_sumo\\simplest_intersection.sumocfg"]

# used to set the display to automatic
pd.options.display.width = 0

traci.start(sumoCmd) # Need to press play in the GUI after this

vehicles_df = pd.DataFrame()

for _ in range(1000):

    traci.simulationStep()

    # Get vehicle count
    traci.vehicle.getIDCount()

    vehicle_ids = traci.vehicle.getIDList()

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

        display(vehicles_df)


traci.close()