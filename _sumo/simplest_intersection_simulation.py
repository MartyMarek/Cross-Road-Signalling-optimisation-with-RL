import os, sys
import pandas as pd
import numpy as np
import traci
from enum import Enum

class SignalStates(Enum):
  GGrrGGrr = 0 # N/S Green, E/W Red
  yyrryyrr = 1 # N/S Yellow, E/W Red
  rrGGrrGG = 2 # N/S Red, E/W Green
  rryyrryy = 3 # N/S Red, E/W Yellow

class SumoSimulation:

    def __init__(self,sumo_binary_path,sumo_config_path,signal_states):

        # SUMO Setup
        self._sumo_binary = sumo_binary_path
        self._sumo_config = sumo_config_path
        self._sumo_command = [self._sumo_binary, "-c", self._sumo_config]
        self._signal_states = signal_states

        # stores the vehicle id's that have moved past the intersection
        self.vehiclesPast = set()
        self.vehiclesPastHistory = set()

        # Store data
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection

    def categorise(self, data):

        # get vehicles travelling horizontally and vertically
        horizontalList = data[data['vehicle_id'].str.contains('south|north')]
        verticalList = data[data['vehicle_id'].str.contains('east|west')]

        horizontal = len(horizontalList.index)
        vertical = len(verticalList.index)

        # get the total wait time for all vehicles
        hTotalTime = horizontalList['accumulated_waiting_time'].sum()
        vTotalTime = verticalList['accumulated_waiting_time'].sum()

        return horizontal, vertical, hTotalTime, vTotalTime

    def beginSimulation(self):
        traci.start(self._sumo_command)  # Need to press play in the GUI after this

    def endSimulation(self):
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("No simulation running.")

    def getSimulationTime(self):

        return traci.simulation.getTime()

    def stepSimulation(self):

        # take the next simulation step (beginSimulation method must be called first)
        traci.simulationStep()

    def getCurrentObservations(self):

        # stores the vehicles in this step of the simulation
        vehicles_df = pd.DataFrame()

        # get all vehicle id's in teh simulation and the vehicles that have left the simulation
        vehicle_ids = list(traci.vehicle.getIDList())
        arrivedVehicles = list(traci.simulation.getArrivedIDList())


        # get any vehicle that have past the intersection on this turn
        for pastVehicle in traci.multientryexit.getLastStepVehicleIDs('intersection_detector'):
            # this set is only used to store vehicles that have passed the interection this step
            self.vehiclesPast.add(pastVehicle)

            # this set keeps all vehicles past so we can delete them from the overall list
            self.vehiclesPastHistory(pastVehicle)

        # now remove the cars that have past the intersection from the list of vehicle id's we are tracking
        for pastVehicle in self.vehiclesPastHistory:
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
        horizontal, vertical, hTime, vTime = self.categorise(vehicles_df)

        # get the traffic light state space
        lightStateString = traci.trafficlight.getRedYellowGreenState('intersection')

        lightState = self._signal_states[lightStateString].value

        # throughput - this can be either the total vehicle past so far or the total / the simulation step
        throughput = len(self.vehiclesPast)
        self.vehiclesPast.clear()

        observations = {
            "traffic": np.array([vertical,horizontal,vTime,hTime,throughput], dtype='int64'),
            "signals": lightState
        }

        return observations

    def collapseSimulationStateToObservations(x):

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

    def updateCurrentSimulationState(self):

        # Get all vehicles
        vehicle_ids = traci.vehicle.getIDList()
        # Get vehicles in intersection
        in_intersection_ids = traci.multientryexit.getLastStepVehicleIDs('intersection_detector')

        # Calculate status for each vehicle
        for vehicle_id in vehicle_ids:
            
            waiting_time = traci.vehicle.getWaitingTime(vehID=vehicle_id)
            accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehID=vehicle_id)
            speed = traci.vehicle.getSpeed(vehID=vehicle_id)
            route = vehicle_id.split(".")[0].replace("flow_","")

            first_frame = False

            if vehicle_id not in list(self._vehicles_state.index.unique()):
                first_frame = True

            if speed < 0.5 and not first_frame:
                stopped = True
            else:
                stopped = False

            # Set default status to None
            status = None
            # Set new throughput to false
            new_throughput = False

            # Calculate status and new_throughput
            if vehicle_id in in_intersection_ids and vehicle_id not in self._vehicles_passed_intersection:
                self._vehicles_passed_intersection.add(vehicle_id)
                status = 'In_Interection'
                new_throughput = True
            elif vehicle_id in in_intersection_ids and vehicle_id in self._vehicles_passed_intersection:
                status = 'In_Interection'
            elif vehicle_id not in in_intersection_ids and vehicle_id in self._vehicles_passed_intersection:
                status = 'Departed_Intersection'
            elif vehicle_id not in in_intersection_ids and vehicle_id not in self._vehicles_passed_intersection:
                status = 'Approaching_Interection'

            # Check if first frame (need this because cars enter the simulation at 0 speed)
            first_frame = False



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

            self._vehicles_state = pd.concat([self._vehicles_state[~self._vehicles_state.index.isin(vehicle_state.index)], vehicle_state])
            self._vehicles_state.update(vehicle_state)
        
    def getCurrentObservations2(self):

        return self._vehicles_state.groupby('route').apply(lambda x: self.collapseSimulationStateToObservations(x=x))
        
    def changeSignalState(self,action):
        signal_string = self._signal_states(action).value
        print("changing state to {0}".format(signal_string))
        traci.trafficlight.setRedYellowGreenState('intersection',signal_string)


