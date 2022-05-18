import os, sys
import pandas as pd
import traci
import categorise as c


class StateSpace:

    def __init__(self, sumo):

        self.categoriser = c.Category()
        # Running Sumo
        sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo', 'tools'))
        #self.sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"
        self.sumoBinary = sumo

        # File to run
        self.sumoCmd = [self.sumoBinary, "-c", "_sumo\\simplest_intersection.sumocfg"]

        # stores the vehicle id's that have moved past the intersection
        self.vehiclesPast = set()


    def beginSimulation(self):
        traci.start(self.sumoCmd)  # Need to press play in the GUI after this

    def endSimulation(self):
        traci.close()


    def getCurrentStateSpace(self):

        # take the next simulation step (beginSimulation method must be called first)
        traci.simulationStep()

        # stores the vehicles in this step of the simulation
        vehicles_df = pd.DataFrame()

        # get all vehicle id's in teh simulation and the vehicles that have left the simulation
        vehicle_ids = list(traci.vehicle.getIDList())
        arrivedVehicles = list(traci.simulation.getArrivedIDList())

        # remove the arrived vehicles
        #for arrived in arrivedVehicles:
        #    if arrived in vehicle_ids:
        #        vehicle_ids.remove(arrived)

        # get the vehicle id's that have moved beyond the detector range and remove them from the list
        #for detected in traci.multientryexit.getLastStepVehicleIDs('intersection_detector'):
        #    if detected in vehicle_ids:
        #        vehicle_ids.remove(detected)

        # get any vehicle that have past the intersection on this turn
        for pastVehicle in traci.multientryexit.getLastStepVehicleIDs('intersection_detector'):
            self.vehiclesPast.add(pastVehicle)

        # now remove the cars that have past the intersection from the list of vehicle id's we are tracking
        for pastVehicle in self.vehiclesPast:
            if pastVehicle in vehicle_ids:
                vehicle_ids.remove(pastVehicle)


        for vehicle_id in vehicle_ids:

            stopped_state = traci.vehicle.getStopState(vehID=vehicle_id)
            waiting_time = traci.vehicle.getWaitingTime(vehID=vehicle_id)
            accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehID=vehicle_id)
            speed = traci.vehicle.getSpeed(vehID=vehicle_id)

            newVehicle = pd.DataFrame(
                {
                    'vehicle_id': [vehicle_id],
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
                # existingIndex = vehicles_df.index[vehicles_df['vehicle_id'] == vehicle_id].tolist()

                if len(indexList) > 0:
                    vehicles_df.iloc[indexList[0]] = newVehicle.iloc[0]
                    continue

            # if the dataframe is empty or does not contain the new vehicle id then insert the new vehicle
            vehicles_df = pd.concat([vehicles_df, newVehicle], ignore_index=True)

        # get the vehicle state space (number of cars waiting horizontally and vertically,
        # and the total accumulated wait time )
        horizontal, vertical, hTime, vTime = self.categoriser.categorise(vehicles_df)

        # get the traffic light state space
        lightStateString = traci.trafficlight.getRedYellowGreenState('intersection')

        lightState = self.categoriser.convertLightStateToInt(lightStateString)

        # throughput - this can be either the total vehicle past so far or the total / the simulation step
        throughput = len(self.vehiclesPast)

        return horizontal, vertical, hTime, vTime, lightState, throughput


