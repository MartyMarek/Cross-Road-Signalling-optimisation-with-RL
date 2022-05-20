import gym
from gym.spaces import Discrete, Box, Dict
import pandas as pd
import numpy as np
from enum import Enum
import random
import traci
from _sumo.simplest_intersection_simulation import SumoSimulation

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
        self.observation_space = Dict({
            "traffic": Box(low=0, high=10000, shape=(5,), dtype=np.int64),
            "signals": Discrete(len(self._simulation._signal_states))
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
        Reset the simulation to the beginning.
        Must return the first observation.
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

        # Return the first observation
        # Signal state needs to be read from the simulation, but do this for now.
        
        # observations = {
        #     "traffic": np.array([0]*5, dtype='int64'),
        #     "signals": 0
        # }
        
        observations = self._simulation.getCurrentObservations()

        return observations

    def step(self, action):
        
        # Step SUMO
        #self._simulation.changeSignalState(action=action) # Getting an error
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        # # New obs
        # observations = {
        #     "traffic": np.array([cars_waiting_ns,cars_waiting_ew,time_waiting_ns,time_waiting_ew,throughput], dtype='int64'),
        #     "signals": signal_state
        # }

        observations = self._simulation.getCurrentObservations()

        # Get cars waiting in N/S direction
        # Get cars approaching in N/S direction
        cars_waiting_ns = observations['traffic'][0]
        # Get cars waiting in E/W direction
        cars_waiting_ew = observations['traffic'][1]
        # Get sum of accumulated wait time for all cars waiting in N/S direction
        time_waiting_ns = observations['traffic'][2]
        # Get sum of accumulated wait time for all cars waiting in E/W direction
        time_waiting_ew = observations['traffic'][3]
        # Get cars that have entered/passed the intersection (throughput)
        throughput = observations['traffic'][4]
        # Get traffic light state
        signal_state = observations['signals']

        # Calculate Reward
        # 10 points for every car that passes the intersection
        # -1 point for every car waiting at the intersection
        # This will likely be a separate class method in the actual implementation
        throughput_reward = throughput * 10
        waiting_punishment = cars_waiting_ns + cars_waiting_ew
        reward = throughput_reward - waiting_punishment
        reward = float(reward)

        # Optionally we can pass additional info, we are not using that for now
        info = {"simulation_time":self._current_simulation_time}

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += (time_waiting_ns + time_waiting_ew)
        # Update total reward
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()
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
