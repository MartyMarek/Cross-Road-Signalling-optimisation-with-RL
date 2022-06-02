import os, sys
import pandas as pd
import numpy as np
import traci
from enum import Enum

class SignalStates(Enum):
    rgrrrgrr = 0
    ryrrryrr = 1
    GrrrGrrr = 2
    yrrryrrr = 3
    rrrgrrrg = 4
    rrryrrry = 5
    rrGrrrGr = 6
    rryrrryr = 7



class SumoSimulation:

    def __init__(self, sumo_binary_path, sumo_config_path, signal_states):

        # SUMO Setup
        self._sumo_binary = sumo_binary_path
        self._sumo_config = sumo_config_path
        self._sumo_command = [self._sumo_binary, "-c", self._sumo_config]
        self._signal_states = signal_states

        # stores the vehicle id's that have moved past the intersection in this step
        self.vehiclesPast = set()

        # stores the vehicle id's that have moved past the intersection during the entire simulation
        self.vehiclesPastHistory = set()

        # stores the vehicle id's for all vehicles that have entered the simulation. This is used to find the
        # vehicles that have entered the simulation this step
        self.allVehicles = set()

        # stores the vehicle id's that entered into the simulation on this step
        self.newVehicles = set()

        # Store data
        self._vehicles_state = pd.DataFrame()  # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set()  # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1



    def beginSimulation(self):
        self._previous_signal_state = None
        self._previous_signal_active_time = 1
        traci.start(self._sumo_command)

    def endSimulation(self):
        self._previous_signal_state = None
        self._previous_signal_active_time = 1
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("No simulation running.")

        self.vehiclesPast.clear()
        self.vehiclesPastHistory.clear()
        self.allVehicles.clear()
        self.newVehicles.clear()

    def getSimulationTime(self):

        return traci.simulation.getTime()

    def stepSimulation(self, step=None):
        # take the next simulation step (beginSimulation method must be called first)
        if step:
            traci.simulationStep(step=step)
        else:
            traci.simulationStep()

    def getCurrentObservations(self):

        # stores the vehicles in this step of the simulation
        vehicles_df = pd.DataFrame()

        # get all vehicle id's in the simulation
        vehicle_ids = list(traci.vehicle.getIDList())

        # find the newest vehicles that have just entered the simulation
        # if our all vehicles set is empty we are at the start of the simulation, so add the first
        # arriving vehicles
        if len(self.allVehicles) == 0:
            for vehicles in vehicle_ids:
                self.allVehicles.add(vehicles)
        else:
            # check the latest vehicles list to the set of all vehicles and mark the difference as
            # the newly arrived vehicles into the simulation
            for vehicle in vehicle_ids:
                if vehicle not in self.allVehicles:
                    self.newVehicles.add(vehicle)

        # get any vehicle that has past the intersection on this turn
        for pastVehicle in traci.multientryexit.getLastStepVehicleIDs('intersection_detector'):
            # this set is only used to store vehicles that have passed the interection this step
            self.vehiclesPast.add(pastVehicle)

            # this set keeps all vehicles past so we can delete them from the overall list
            self.vehiclesPastHistory.add(pastVehicle)

        # now remove the cars that have past the intersection from the list of vehicle id's we are tracking
        for pastVehicle in self.vehiclesPastHistory:
            if pastVehicle in vehicle_ids:
                vehicle_ids.remove(pastVehicle)

        # also remove the newly arrived vehicles as they have a speed of 0 on their first turn
        for vehicle in self.newVehicles:
            if vehicle in vehicle_ids:
                vehicle_ids.remove(vehicle)

        # the left over vehicle id's should be the ones that are either approaching the lights or stopped at the lights
        for vehicle_id in vehicle_ids:

            waiting_time = traci.vehicle.getWaitingTime(vehID=vehicle_id)
            accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehID=vehicle_id)
            speed = traci.vehicle.getSpeed(vehID=vehicle_id)

            newVehicle = pd.DataFrame(
                {
                    'vehicle_id': [vehicle_id],
                    'waiting_time': [waiting_time],
                    'accumulated_waiting_time': [accumulated_waiting_time],
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
        observation = self.categorise(vehicles_df)

        # get the traffic light state space
        lightStateString = traci.trafficlight.getRedYellowGreenState('intersection')
        current_signal_state = self._signal_states[lightStateString].value

        # Get the previous signal state
        previous_signal_state = self._previous_signal_state
        if not previous_signal_state:
            previous_signal_state = current_signal_state
        # Update previous signal state with current signal
        self._previous_signal_state = current_signal_state
        # Get previous signal active time
        previous_signal_active_time = self._previous_signal_active_time
        # Increase the previous signal active time by 1
        if current_signal_state == previous_signal_state:
            self._previous_signal_active_time += 1
        else:
            self._previous_signal_active_time = 1

        lightStatusTime = self.binLightStatusTime(self._previous_signal_active_time)

        # throughput - is now only the number of cars that have passed the intersection on this turn
        throughput = self.binVehicles(len(self.vehiclesPast))

        # add throughput to our observation
        observation.append(throughput)

        # add lightState to observation
        observation.append(current_signal_state)
        observation.append(previous_signal_state)
        observation.append(lightStatusTime)

        # add the newly arrived vehicles to the allvehicles list so next turn they are counted
        self.allVehicles.update(self.newVehicles)

        # reset the sets that track step by step
        self.vehiclesPast.clear()
        self.newVehicles.clear()

        # return the current observation
        return tuple(observation)


    def getSignalState(self):
        return self._signal_states[traci.trafficlight.getRedYellowGreenState(tlsID='intersection')].value

    def changeSignalState(self, action):
        signal_string = self._signal_states(action).name
        traci.trafficlight.setRedYellowGreenState('intersection', signal_string)


    def categorise(self, data):

        # get vehicles travelling horizontally and vertically
        verticalList = data[data['vehicle_id'].str.contains('north_to_south|north_to_east|south_to_north|south_to_west')]
        verticalTurnRightList = data[data['vehicle_id'].str.contains('north_to_west|south_to_east')]
        horizontalList = data[data['vehicle_id'].str.contains('west_to_east|west_to_north|east_to_west|east_to_south')]
        horizontalTurnRightList = data[data['vehicle_id'].str.contains('west_to_south|east_to_north')]

        # binning the number of vehicles
        horizontal = self.binVehicles(len(horizontalList.index))
        horizontalRight = self.binVehicles(len(horizontalTurnRightList.index))
        vertical = self.binVehicles(len(verticalList.index))
        verticalRight = self.binVehicles(len(verticalTurnRightList.index))

        total = len(horizontalList.index) + len(horizontalTurnRightList.index) + \
                len(verticalList.index) + len(verticalTurnRightList.index)

        totalBinned = self.binTotalVehicles(total)

        # get the total wait time for all vehicles
        horizontalTotalTime = self.binAccumulatedWaitTime(horizontalList['accumulated_waiting_time'].sum())
        horizontalRightTotalTime = self.binAccumulatedWaitTime(horizontalTurnRightList['accumulated_waiting_time'].sum())
        verticalTotalTime = self.binAccumulatedWaitTime(verticalList['accumulated_waiting_time'].sum())
        verticalRightTotalTime = self.binAccumulatedWaitTime(verticalTurnRightList['accumulated_waiting_time'].sum())

        # create an array with the results
        return [totalBinned]


    def binLightStatusTime(self, statusTime):
        if statusTime < 4:
            return 0
        elif statusTime < 10:
            return 1
        elif statusTime < 15:
            return 2
        else:
            return 3

    def binAccumulatedWaitTime(self, waitTime):
        if waitTime < 30:
            return 0
        elif waitTime < 60:
            return 1
        elif waitTime < 120:
            return 2
        else:
            return 3

    def binVehicles(self, vehicles):
        if vehicles < 3:
            return 0
        elif vehicles < 6:
            return 1
        elif vehicles < 9:
            return 2
        else:
            return 3

    def binTotalVehicles(self, vehicles):
        if vehicles < 10:
            return 0
        elif vehicles < 20:
            return 1
        elif vehicles < 30:
            return 2
        else:
            return 3