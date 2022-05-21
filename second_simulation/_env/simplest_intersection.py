from this import d
import gym
from gym.spaces import Discrete, Box, Dict
import pandas as pd
import numpy as np
from enum import Enum
import random
import traci
from _sumo.simplest_intersection_simulation import SumoSimulation
from _env.reward import *



class SimplestIntersection(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,simulation: SumoSimulation,max_simulation_seconds):

        super(SimplestIntersection, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds

        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''
        
        self.action_space = Discrete(len(self._simulation._signal_states))

        ## Observation space
        '''
        Observations corresponding to the following metrics in the latest timestep:
        Traffic
            - Number of cars waiting at the intersection in the N/S direction
            - Number of cars waiting at the intersection in the E/W direction
            - Sum of accumulated waiting time for all cars waiting at the intersection in the N/S directions
            - Sum of accumulated waiting time for all cars waiting at the intersection in the E/W directions
            - Number of new vehicles that have entered/passed the intersection (throughput)
        Signals
            - Traffic light state 
        '''
        # self.observation_space = Dict({
        #     "traffic": Box(low=0, high=10000, shape=(5,4), dtype=np.int64),
        #     "signals": Discrete(len(self._simulation._signal_states))
        # })
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(20,),dtype=np.float64),
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
            "traffic":np.zeros((20,),dtype=np.float64),
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

        # Calculate Reward
        throughput = traffic['new_throughput'].sum()
        reward = calculate_reward_01(throughput=throughput)

        # Optionally we can pass additional info, we are not using that for now
        info = {
            "traffic": traffic,
            "signal_state": current_signal_state,
            "previous_signal_state": previous_signal_state,
            "previous_signal_active_time": previous_signal_active_time,
            "simulation_time":self._current_simulation_time
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
        else:
            done = False

        # observations = {
        #     "traffic": traffic.values.flatten(),
        #     "signals": signals
        # }

        observations = {
            "traffic": traffic.values.flatten(),
            "current_signal": current_signal_state,
            "previous_signal": int(previous_signal_state),
            "previous_signal_active_time": np.array([previous_signal_active_time],dtype=np.int64)
        }

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


