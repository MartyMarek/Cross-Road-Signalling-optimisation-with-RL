from this import d
import gym
from gym.spaces import Discrete, Box, Dict
import pandas as pd
import numpy as np
from enum import Enum
import random
import traci
from final_simulation._sumo.simplest_intersection_simulation import SignalStates, SumoSimulation
from final_simulation._env.reward import *
from final_simulation.datastore import *


class RealIntersection7(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(RealIntersection7, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds
        
        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''

        # action space
        self.action_space = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(60,),dtype=np.float64),
            "current_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal_active_time": Box(low=0, high=10000, shape=(1,),dtype=np.int64)
        })
        
        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = 0
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # used to store each state and save to a file
        self.datastore = DataStore()


    def reset(self):
        """
        Reset the simulation to the beginning. Must return the first observation.
        """

        # Reset SUMO
        ## Close any existing session
        self._simulation.endSimulation()
        
        ## Start new session
        self._simulation.beginSimulation()
        self._simulation.stepSimulation()

        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = self._simulation.getSimulationTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        observations = {
            "traffic":np.zeros((60,),dtype=np.float64),
            "current_signal": self._simulation.getSignalState(),
            "previous_signal": self._simulation.getSignalState(),
            "previous_signal_active_time": np.array([self._simulation._previous_signal_active_time],dtype=np.int64)
        }

        return observations

    def step(self, action):
        
        # Step SUMO
        self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        traffic,current_signal_state,previous_signal_state,previous_signal_active_time = self._simulation.getCurrentObservations()

        # save the observation to a datastore
        traffic_record = traffic.values.flatten()
        traffic_record = np.insert(traffic_record, 0, self._current_time_step)
        #self.datastore.addNewRecord(traffic_record) # TODO Something here is broken

        observations = {
            "traffic": traffic.values.flatten(),
            "current_signal": current_signal_state,
            "previous_signal": int(previous_signal_state),
            "previous_signal_active_time": np.array([previous_signal_active_time], dtype=np.int64)
        }

        # Calculate Reward
        throughput = traffic['new_throughput'].sum()


        reward = calculate_reward_07(
            throughput=traffic['new_throughput'].sum(),
            cars_waiting=traffic['stopped_cars'].sum(),
            accumulated_wait_time=traffic['accumulated_waiting_time'].sum(),
            current_signal_state=current_signal_state,
            previous_signal_state=previous_signal_state,
            previous_signal_active_time=previous_signal_active_time
        )

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time,
            "reward": reward
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += traffic['accumulated_waiting_time'].sum()
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            self.datastore.saveCurrentRecord()
        else:
            done = False

        return observations, reward, done, info


    def render(self, mode='console'):

        if mode == 'console':
            print(
            '''
            Total Time Steps: {0}
            Previous Signal: {1}
            Total Signal Changes: {2}
            Total Throughput: {3}
            Total Wait Time: {4}
            Total Reward: {5}
            '''.format(
                self._current_time_step,
                self._previous_signal,
                self._total_signal_changes,
                self._total_throughput,
                self._total_wait_time,
                self._total_reward
            )
            )
            
        else:
            raise NotImplementedError()
        # agent is represented as a cross, rest as a dot
        #print("Position: ",self.agent_pos)
        #print("." * self.agent_pos, end="")
        #print("x", end="")
        #print("." * (self.grid_size - self.agent_pos))

    def close(self):
        # Close any existing session
        self._simulation.endSimulation()

class RealIntersection8(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(RealIntersection8, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds
        
        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''

        # action space
        self.action_space = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(60,),dtype=np.float64),
            "current_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal_active_time": Box(low=0, high=10000, shape=(1,),dtype=np.int64)
        })
        
        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = 0
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # used to store each state and save to a file
        self.datastore = DataStore()


    def reset(self):
        """
        Reset the simulation to the beginning. Must return the first observation.
        """

        # Reset SUMO
        ## Close any existing session
        self._simulation.endSimulation()
        
        ## Start new session
        self._simulation.beginSimulation()
        self._simulation.stepSimulation()

        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = self._simulation.getSimulationTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        observations = {
            "traffic":np.zeros((60,),dtype=np.float64),
            "current_signal": self._simulation.getSignalState(),
            "previous_signal": self._simulation.getSignalState(),
            "previous_signal_active_time": np.array([self._simulation._previous_signal_active_time],dtype=np.int64)
        }

        return observations

    def step(self, action):
        
        # Step SUMO
        self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        traffic,current_signal_state,previous_signal_state,previous_signal_active_time = self._simulation.getCurrentObservations()

        # save the observation to a datastore
        traffic_record = traffic.values.flatten()
        traffic_record = np.insert(traffic_record, 0, self._current_time_step)
        #self.datastore.addNewRecord(traffic_record) # TODO Something here is broken

        observations = {
            "traffic": traffic.values.flatten(),
            "current_signal": current_signal_state,
            "previous_signal": int(previous_signal_state),
            "previous_signal_active_time": np.array([previous_signal_active_time], dtype=np.int64)
        }

        # Calculate Reward
        throughput = traffic['new_throughput'].sum()

        reward = calculate_reward_08(
            throughput=traffic['new_throughput'].sum(),
            cars_waiting=traffic['stopped_cars'].sum(),
            accumulated_wait_time=traffic['accumulated_waiting_time'].sum(),
            current_signal_state=current_signal_state,
            previous_signal_state=previous_signal_state,
            previous_signal_active_time=previous_signal_active_time
        )

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time,
            "reward": reward
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += traffic['accumulated_waiting_time'].sum()
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            self.datastore.saveCurrentRecord()
        else:
            done = False

        return observations, reward, done, info


    def render(self, mode='console'):

        if mode == 'console':
            print(
            '''
            Total Time Steps: {0}
            Previous Signal: {1}
            Total Signal Changes: {2}
            Total Throughput: {3}
            Total Wait Time: {4}
            Total Reward: {5}
            '''.format(
                self._current_time_step,
                self._previous_signal,
                self._total_signal_changes,
                self._total_throughput,
                self._total_wait_time,
                self._total_reward
            )
            )
            
        else:
            raise NotImplementedError()
        # agent is represented as a cross, rest as a dot
        #print("Position: ",self.agent_pos)
        #print("." * self.agent_pos, end="")
        #print("x", end="")
        #print("." * (self.grid_size - self.agent_pos))

    def close(self):
        # Close any existing session
        self._simulation.endSimulation()

class RealIntersection9(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(RealIntersection9, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds
        
        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''

        # action space
        self.action_space = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(60,),dtype=np.float64),
            "current_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal_active_time": Box(low=0, high=10000, shape=(1,),dtype=np.int64)
        })
        
        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = 0
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # used to store each state and save to a file
        self.datastore = DataStore()


    def reset(self):
        """
        Reset the simulation to the beginning. Must return the first observation.
        """

        # Reset SUMO
        ## Close any existing session
        self._simulation.endSimulation()
        
        ## Start new session
        self._simulation.beginSimulation()
        self._simulation.stepSimulation()

        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = self._simulation.getSimulationTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        observations = {
            "traffic":np.zeros((60,),dtype=np.float64),
            "current_signal": self._simulation.getSignalState(),
            "previous_signal": self._simulation.getSignalState(),
            "previous_signal_active_time": np.array([self._simulation._previous_signal_active_time],dtype=np.int64)
        }

        return observations

    def step(self, action):
        
        # Step SUMO
        self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        traffic,current_signal_state,previous_signal_state,previous_signal_active_time = self._simulation.getCurrentObservations()

        # save the observation to a datastore
        traffic_record = traffic.values.flatten()
        traffic_record = np.insert(traffic_record, 0, self._current_time_step)
        #self.datastore.addNewRecord(traffic_record) # TODO Something here is broken

        observations = {
            "traffic": traffic.values.flatten(),
            "current_signal": current_signal_state,
            "previous_signal": int(previous_signal_state),
            "previous_signal_active_time": np.array([previous_signal_active_time], dtype=np.int64)
        }

        # Calculate Reward
        throughput = traffic['new_throughput'].sum()

        reward = calculate_reward_09(
            throughput=traffic['new_throughput'].sum(),
            cars_waiting=traffic['stopped_cars'].sum(),
            accumulated_wait_time=traffic['accumulated_waiting_time'].sum(),
            current_signal_state=current_signal_state,
            previous_signal_state=previous_signal_state,
            previous_signal_active_time=previous_signal_active_time
        )

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time,
            "reward": reward
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += traffic['accumulated_waiting_time'].sum()
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            self.datastore.saveCurrentRecord()
        else:
            done = False

        return observations, reward, done, info


    def render(self, mode='console'):

        if mode == 'console':
            print(
            '''
            Total Time Steps: {0}
            Previous Signal: {1}
            Total Signal Changes: {2}
            Total Throughput: {3}
            Total Wait Time: {4}
            Total Reward: {5}
            '''.format(
                self._current_time_step,
                self._previous_signal,
                self._total_signal_changes,
                self._total_throughput,
                self._total_wait_time,
                self._total_reward
            )
            )
            
        else:
            raise NotImplementedError()
        # agent is represented as a cross, rest as a dot
        #print("Position: ",self.agent_pos)
        #print("." * self.agent_pos, end="")
        #print("x", end="")
        #print("." * (self.grid_size - self.agent_pos))

    def close(self):
        # Close any existing session
        self._simulation.endSimulation()

class RealIntersection10(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(RealIntersection10, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds
        
        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''

        # action space
        self.action_space = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(60,),dtype=np.float64),
            "current_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal_active_time": Box(low=0, high=10000, shape=(1,),dtype=np.int64)
        })
        
        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = 0
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # used to store each state and save to a file
        self.datastore = DataStore()


    def reset(self):
        """
        Reset the simulation to the beginning. Must return the first observation.
        """

        # Reset SUMO
        ## Close any existing session
        self._simulation.endSimulation()
        
        ## Start new session
        self._simulation.beginSimulation()
        self._simulation.stepSimulation()

        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = self._simulation.getSimulationTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        observations = {
            "traffic":np.zeros((60,),dtype=np.float64),
            "current_signal": self._simulation.getSignalState(),
            "previous_signal": self._simulation.getSignalState(),
            "previous_signal_active_time": np.array([self._simulation._previous_signal_active_time],dtype=np.int64)
        }

        return observations

    def step(self, action):
        
        # Step SUMO
        self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        traffic,current_signal_state,previous_signal_state,previous_signal_active_time = self._simulation.getCurrentObservations()

        # save the observation to a datastore
        traffic_record = traffic.values.flatten()
        traffic_record = np.insert(traffic_record, 0, self._current_time_step)
        #self.datastore.addNewRecord(traffic_record) # TODO Something here is broken

        observations = {
            "traffic": traffic.values.flatten(),
            "current_signal": current_signal_state,
            "previous_signal": int(previous_signal_state),
            "previous_signal_active_time": np.array([previous_signal_active_time], dtype=np.int64)
        }

        # Calculate Reward
        throughput = traffic['new_throughput'].sum()

        reward = calculate_reward_10(
            throughput=traffic['new_throughput'].sum(),
            cars_waiting=traffic['stopped_cars'].sum(),
            accumulated_wait_time=traffic['accumulated_waiting_time'].sum(),
            current_signal_state=current_signal_state,
            previous_signal_state=previous_signal_state,
            previous_signal_active_time=previous_signal_active_time
        )

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time,
            "reward": reward
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += traffic['accumulated_waiting_time'].sum()
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            self.datastore.saveCurrentRecord()
        else:
            done = False

        return observations, reward, done, info


    def render(self, mode='console'):

        if mode == 'console':
            print(
            '''
            Total Time Steps: {0}
            Previous Signal: {1}
            Total Signal Changes: {2}
            Total Throughput: {3}
            Total Wait Time: {4}
            Total Reward: {5}
            '''.format(
                self._current_time_step,
                self._previous_signal,
                self._total_signal_changes,
                self._total_throughput,
                self._total_wait_time,
                self._total_reward
            )
            )
            
        else:
            raise NotImplementedError()
        # agent is represented as a cross, rest as a dot
        #print("Position: ",self.agent_pos)
        #print("." * self.agent_pos, end="")
        #print("x", end="")
        #print("." * (self.grid_size - self.agent_pos))

    def close(self):
        # Close any existing session
        self._simulation.endSimulation()

class RealIntersection11(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(RealIntersection11, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds
        
        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''

        # action space
        self.action_space = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(60,),dtype=np.float64),
            "current_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal": Discrete(len(self._simulation._signal_states)),
            "previous_signal_active_time": Box(low=0, high=10000, shape=(1,),dtype=np.int64)
        })
        
        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = 0
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # used to store each state and save to a file
        self.datastore = DataStore()


    def reset(self):
        """
        Reset the simulation to the beginning. Must return the first observation.
        """

        # Reset SUMO
        ## Close any existing session
        self._simulation.endSimulation()
        
        ## Start new session
        self._simulation.beginSimulation()
        self._simulation.stepSimulation()

        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = self._simulation.getSimulationTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        observations = {
            "traffic":np.zeros((60,),dtype=np.float64),
            "current_signal": self._simulation.getSignalState(),
            "previous_signal": self._simulation.getSignalState(),
            "previous_signal_active_time": np.array([self._simulation._previous_signal_active_time],dtype=np.int64)
        }

        return observations

    def step(self, action):
        
        # Step SUMO
        self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        traffic,current_signal_state,previous_signal_state,previous_signal_active_time = self._simulation.getCurrentObservations()

        # save the observation to a datastore
        traffic_record = traffic.values.flatten()
        traffic_record = np.insert(traffic_record, 0, self._current_time_step)
        #self.datastore.addNewRecord(traffic_record) # TODO Something here is broken

        observations = {
            "traffic": traffic.values.flatten(),
            "current_signal": current_signal_state,
            "previous_signal": int(previous_signal_state),
            "previous_signal_active_time": np.array([previous_signal_active_time], dtype=np.int64)
        }

        # Calculate Reward
        throughput = traffic['new_throughput'].sum()

        reward = calculate_reward_11(
            throughput=traffic['new_throughput'].sum(),
            cars_waiting=traffic['stopped_cars'].sum(),
            accumulated_wait_time=traffic['accumulated_waiting_time'].sum(),
            current_signal_state=current_signal_state,
            previous_signal_state=previous_signal_state,
            previous_signal_active_time=previous_signal_active_time,
            signal_states=SignalStates
        )

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time,
            "reward": reward
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += traffic['accumulated_waiting_time'].sum()
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            self.datastore.saveCurrentRecord()
        else:
            done = False

        return observations, reward, done, info


    def render(self, mode='console'):

        if mode == 'console':
            print(
            '''
            Total Time Steps: {0}
            Previous Signal: {1}
            Total Signal Changes: {2}
            Total Throughput: {3}
            Total Wait Time: {4}
            Total Reward: {5}
            '''.format(
                self._current_time_step,
                self._previous_signal,
                self._total_signal_changes,
                self._total_throughput,
                self._total_wait_time,
                self._total_reward
            )
            )
            
        else:
            raise NotImplementedError()
        # agent is represented as a cross, rest as a dot
        #print("Position: ",self.agent_pos)
        #print("." * self.agent_pos, end="")
        #print("x", end="")
        #print("." * (self.grid_size - self.agent_pos))

    def close(self):
        # Close any existing session
        self._simulation.endSimulation()

class RealIntersectionSimpleObs12(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(RealIntersectionSimpleObs12, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds
        
        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''

        # action space
        self.action_space = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = Box(low=0, high=1000, shape=(8,),dtype=np.int64)
        
        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = 0
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # used to store each state and save to a file
        self.datastore = DataStore()


    def reset(self):
        """
        Reset the simulation to the beginning. Must return the first observation.
        """

        # Reset SUMO
        ## Close any existing session
        self._simulation.endSimulation()
        
        ## Start new session
        self._simulation.beginSimulation()
        self._simulation.stepSimulation()

        # Reset counters
        self._current_time_step = 1
        self._current_simulation_time = self._simulation.getSimulationTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None


        observations = np.zeros((8,),dtype=np.int64)

        return observations

    def step(self, action):
        
        # Step SUMO
        self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        traffic,throughput,current_signal_state,previous_signal_state,previous_signal_active_time = self._simulation.getCurrentObservations()

        observations = np.append(traffic.to_numpy(dtype=np.int64),np.array([throughput,current_signal_state,previous_signal_state,previous_signal_active_time],dtype=np.int64))
        
        # Calculate Reward
        reward = calculate_reward_12(
            throughput=throughput,
            cars_waiting=traffic['stopped_cars'].sum(),
            current_signal_state=current_signal_state,
            previous_signal_state=previous_signal_state,
            previous_signal_active_time=previous_signal_active_time,
            signal_states=SignalStates
        )

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time,
            "reward": reward
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        #self._total_wait_time += traffic['accumulated_waiting_time'].sum()
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            self.datastore.saveCurrentRecord()
        else:
            done = False

        return observations, reward, done, info


    def render(self, mode='console'):

        if mode == 'console':
            print(
            '''
            Total Time Steps: {0}
            Total Signal Changes: {1}
            Total Throughput: {2}
            Total Reward: {3}
            '''.format(
                self._current_time_step,
                self._total_signal_changes,
                self._total_throughput,
                self._total_reward
            )
            )
            
        else:
            raise NotImplementedError()
        # agent is represented as a cross, rest as a dot
        #print("Position: ",self.agent_pos)
        #print("." * self.agent_pos, end="")
        #print("x", end="")
        #print("." * (self.grid_size - self.agent_pos))

    def close(self):
        # Close any existing session
        self._simulation.endSimulation()
