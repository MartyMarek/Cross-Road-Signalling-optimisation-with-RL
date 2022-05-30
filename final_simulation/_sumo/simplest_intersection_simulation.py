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

    def __init__(self,sumo_binary_path,sumo_config_path,signal_states):

        # SUMO Setup
        self._sumo_binary = sumo_binary_path
        self._sumo_config = sumo_config_path
        self._sumo_command = [self._sumo_binary, "-c", self._sumo_config]
        self._signal_states = signal_states
        
        
        # Store data
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1

    def beginSimulation(self):
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1
        
        traci.start(self._sumo_command)  # Need to press play in the GUI after this

        # Get a list of routes to build a standard observation frame
        # Required for when no cars from a specific route are in the simulation at a given time step
        self._routes = set()
        for route in traci.route.getIDList():
            self._routes.add(route.split(".")[0].replace("!","").replace("flow_",""))

    def endSimulation(self):
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1

        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("No simulation running.")

    def getSimulationTime(self):
        return traci.simulation.getTime()

    def stepSimulation(self,step=None):
        # take the next simulation step (beginSimulation method must be called first)
        if step:
            traci.simulationStep(step=step)
        else:
            traci.simulationStep()


    def collapseSimulationStateToObservations(self,x):
        '''
        This is an aggregation function that takes a pandas dataframe grouped by route as input (x).
        The intention is to output the following for each route:
        - Approaching Cars
        - Stopped Cars
        - Status (Approaching_Intersection, In_Intersection, Departed_Intersection)
        - Average Speed
        - Accumulated Waiting Time
        - New Throughput
        '''

        # Create empty dictionary
        output_dict = dict()
        # Get number of vehicles approaching the intersection
        output_dict['approaching_cars'] = x.loc[x['status'] == 'Approaching_Interection'].index.nunique()
        # Get number of vehicles approaching the intersection that are stopped
        output_dict['stopped_cars'] = x.loc[
            (x['status'] == 'Approaching_Interection') & 
            (x['stopped'] == True)
        ].index.nunique()
        # Get the average speed for vehicles either approaching the intersection or in the intersection
        output_dict['average_speed'] = x.loc[
            ((x['status'] == 'Approaching_Interection') |
            (x['status'] == 'In_Interection')) &
            (x['first_frame'] == False),
            'speed'
        ].mean()
        # Replace NaN average speeds with 0
        if np.isnan(output_dict['average_speed']):
            output_dict['average_speed'] = 0
        # Get accumulated waiting time for vehicles approaching the intersection
        output_dict['accumulated_waiting_time'] = x.loc[x['status'] == 'Approaching_Interection','accumulated_waiting_time'].sum()
        # Get number of vehicles that are new throughput
        output_dict['new_throughput'] = x.loc[x['new_throughput'] == True].index.nunique()

        # Return a pandas series for each group
        # This is combined to a dataframe when the aggregate function is finished
        return pd.Series(data=output_dict)


    def getCurrentObservations(self):

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

            # The two steps below are equivalent to an upsert
            # Concatenate new vehicles to the vehicles state data frame
            self._vehicles_state = pd.concat([self._vehicles_state[~self._vehicles_state.index.isin(vehicle_state.index)], vehicle_state])
            # Update values in the vehicles state data frame with latest values
            self._vehicles_state.update(vehicle_state)

        # Group vehicles in vehicles state data frame by route and calculate desired observations
        traffic = self._vehicles_state.groupby('route').apply(lambda x: self.collapseSimulationStateToObservations(x=x))
        # Create standard traffic observation space
        traffic_standard = pd.DataFrame(
            columns=[
                'approaching_cars',
                'stopped_cars',
                'average_speed',
                'accumulated_waiting_time',
                'new_throughput'
            ],
            index=self._routes
        ).fillna(0).sort_index()
        traffic_standard.index.name = 'routes'
        # Update standard traffic observation space with actual values
        traffic_standard.update(traffic)
        # Get the current signal state
        current_signal_state = self._signal_states[traci.trafficlight.getRedYellowGreenState(tlsID='intersection')].value
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
            
        return traffic_standard,current_signal_state,previous_signal_state,previous_signal_active_time

    def getSignalState(self):
        return self._signal_states[traci.trafficlight.getRedYellowGreenState(tlsID='intersection')].value

    def changeSignalState(self,action):
        signal_string = self._signal_states(action).name
        traci.trafficlight.setRedYellowGreenState('intersection',signal_string)

class SumoSimulationSimpleObs:

    def __init__(self,sumo_binary_path,sumo_config_path,signal_states):

        # SUMO Setup
        self._sumo_binary = sumo_binary_path
        self._sumo_config = sumo_config_path
        self._sumo_command = [self._sumo_binary, "-c", self._sumo_config]
        self._signal_states = signal_states
        
        
        # Store data
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1

    def beginSimulation(self):
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1
        
        traci.start(self._sumo_command)  # Need to press play in the GUI after this

        # Get a list of routes to build a standard observation frame
        # Required for when no cars from a specific route are in the simulation at a given time step
        self._entries = set()
        # for route in traci.route.getIDList():
        #     self._routes.add(route.split(".")[0].replace("!","").replace("flow_",""))
        self._entries.add("north")
        self._entries.add("east")
        self._entries.add("south")
        self._entries.add("west")

    def endSimulation(self):
        self._vehicles_state = pd.DataFrame() # Updated every step with the current state of all vehicles
        self._vehicles_passed_intersection = set() # A set of vehicles that have passed the intersection
        self._previous_signal_state = None
        self._previous_signal_active_time = 1

        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("No simulation running.")

    def getSimulationTime(self):
        return traci.simulation.getTime()

    def stepSimulation(self,step=None):
        # take the next simulation step (beginSimulation method must be called first)
        if step:
            traci.simulationStep(step=step)
        else:
            traci.simulationStep()


    def collapseSimulationStateToObservations(self,x):
        '''
        This is an aggregation function that takes a pandas dataframe grouped by route as input (x).
        The intention is to output the following for each route:
        - Approaching Cars
        - Stopped Cars
        - Status (Approaching_Intersection, In_Intersection, Departed_Intersection)
        - Average Speed
        - Accumulated Waiting Time
        - New Throughput
        '''

        # Create empty dictionary
        output_dict = dict()
        # Get number of vehicles approaching the intersection that are stopped
        output_dict['stopped_cars'] = x.loc[
            (x['status'] == 'Approaching_Interection') & 
            (x['stopped'] == True)
        ].index.nunique()
        # Get number of vehicles that are new throughput
        output_dict['new_throughput'] = x.loc[x['new_throughput'] == True].index.nunique()

        # Return a pandas series for each group
        # This is combined to a dataframe when the aggregate function is finished
        return pd.Series(data=output_dict)


    def getCurrentObservations(self):

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
            entry = route.split("_")[0]

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

            vehicle_state = pd.DataFrame(
                {
                    #'vehicle_id': [vehicle_id],
                    'route': [route],
                    'entry': [entry],
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

            # The two steps below are equivalent to an upsert
            # Concatenate new vehicles to the vehicles state data frame
            self._vehicles_state = pd.concat([self._vehicles_state[~self._vehicles_state.index.isin(vehicle_state.index)], vehicle_state])
            # Update values in the vehicles state data frame with latest values
            self._vehicles_state.update(vehicle_state)

        # Group vehicles in vehicles state data frame by route and calculate desired observations
        traffic = self._vehicles_state.groupby('entry').apply(lambda x: self.collapseSimulationStateToObservations(x=x))
        # Create standard traffic observation space
        traffic_standard = pd.DataFrame(
            columns=[
                'stopped_cars',
                'new_throughput'
            ],
            index=self._entries
        ).fillna(0).sort_index()
        traffic_standard.index.name = 'entry'
        # Update standard traffic observation space with actual values
        traffic_standard.update(traffic)
        # Calculate throughput
        throughput = traffic_standard['new_throughput'].sum()
        # Drop throughput
        traffic_standard.drop(labels=['new_throughput'],axis='columns',inplace=True)
        # Get the current signal state
        current_signal_state = self._signal_states[traci.trafficlight.getRedYellowGreenState(tlsID='intersection')].value
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
            
        return traffic_standard,throughput,current_signal_state,previous_signal_state,previous_signal_active_time

    def getSignalState(self):
        return self._signal_states[traci.trafficlight.getRedYellowGreenState(tlsID='intersection')].value

    def changeSignalState(self,action):
        signal_string = self._signal_states(action).name
        traci.trafficlight.setRedYellowGreenState('intersection',signal_string)


