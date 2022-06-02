from this import d
import gym
from gym.spaces import Discrete, Box, Dict
import pandas as pd
import numpy as np
from enum import Enum
import random
import traci
from _sumo.simplest_intersection_simulation import SignalStates, SumoSimulation
from _env.reward import *
from datastore import *


class SimplestIntersection(gym.Env):
    """
    Custom Environment that follows gym interface. This one is used by the q learning algorithm written from scratch.
    """

    def __init__(self, simulation: SumoSimulation, max_simulation_seconds):

        super(SimplestIntersection, self).__init__()

        # SUMO Setup
        self._simulation = simulation
        self._max_simulation_seconds = max_simulation_seconds

        # action space
        self.actions = Discrete(len(self._simulation._signal_states))

        # observation space
        self.observation_space = 4096

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

        return (0,0,0,0,0)

    def step(self, action):

        # Step SUMO
        self._simulation.changeSignalState(action=action)
        self._simulation.stepSimulation()

        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = self._simulation.getSimulationTime()

        observation = self._simulation.getCurrentObservations()


        cars_waiting = observation[0]
        throughput = observation[1]
        current_signal_state = observation[2]
        previous_signal_state = observation[3]
        previous_signal_active_time = observation[4]


        reward = simple_reward_13(throughput, cars_waiting, current_signal_state,
                                  previous_signal_state, previous_signal_active_time, SignalStates)

        info = {
            "throughput": throughput
        }

        ## Update values
        # Update total signal changes
        if self._simulation._signal_states(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = self._simulation._signal_states(action).name

        # Update total throughput and reward
        self._total_throughput += throughput
        self._total_reward += reward

        ## Check if simulation is finished
        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            self._simulation.endSimulation()

            # save observations to a file (This will also reset the datastore)
            #self.datastore.saveCurrentRecord()
        else:
            done = False

        return observation, reward, done, info


    def render(self, mode='console'):
        return


    def close(self):
        # Close any existing session
        self._simulation.endSimulation()


