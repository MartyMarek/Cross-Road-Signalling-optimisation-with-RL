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
import os


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
        self._records_steps = list()
        self._records_rewards = list()
        self._records_throughputs = list()
        self._records_waiting_times = list()
        self._records_cars_waiting = list()
        self._records_signal_changes = list()

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

        # Data store
        self._records_steps = list()
        self._records_rewards = list()
        self._records_throughputs = list()
        self._records_waiting_times = list()
        self._records_cars_waiting = list()
        self._records_signal_changes = list()

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

        signal_change_marker = 0
        if current_signal_state != previous_signal_state:
            signal_change_marker = 1


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

        # Update data store
        self._records_steps.append(self._current_time_step - 1)
        self._records_rewards.append(reward)
        self._records_throughputs.append(throughput)
        self._records_waiting_times.append(0) # TODO Add the actual waiting times variable
        self._records_cars_waiting.append(cars_waiting)
        self._records_signal_changes.append(signal_change_marker)

        return observation, reward, done, info


    def render(self, mode='console'):
        return


    def close(self):
        # Close any existing session
        self._simulation.endSimulation()

    def save_metrics(self,episode,model_name,log_dir):

        os.makedirs(log_dir, exist_ok=True)
        output_path = "{0}\\eval_metrics.csv".format(log_dir)
        

        data = dict(
            steps = self._records_steps,
            reward = self._records_rewards,
            throughput = self._records_throughputs,
            waiting_time = self._records_waiting_times,
            cars_waiting = self._records_cars_waiting,
            signal_changes = self._records_signal_changes
        )

        complete_monitor_df = pd.DataFrame(data=data)
        complete_monitor_df['episode'] = episode
        complete_monitor_df['model_name'] = model_name
        complete_monitor_df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)



