import gym
from gym.spaces import Discrete, Box, Dict
from stable_baselines3.common.env_checker import check_env
import pandas as pd
import numpy as np
from enum import Enum
import random
import os, sys
from torch import sign
import traci

class TrafficLightStates(Enum):
  GrGr = 0 # N/S Green, E/W Red
  rGrG = 1 # N/S Red, E/W Green

class SimplestIntersection(gym.Env):
    """
    Custom Environment that follows gym interface.
    Implementing the simplest intersection. 
    """
    # Define metadata
    metadata = {'render.modes': ['console','human']}

    # Define constants for clearer code


    def __init__(self,sumo_binary_path,sumo_config_path,max_simulation_seconds):

        super(SimplestIntersection, self).__init__()

        # Spaces
        ## Define action space
        '''
        Discrete actions corresponding to each possible traffic light state for the intersection
        '''
        
        self.action_space = Discrete(len(TrafficLightStates))

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
            "signals": Discrete(len(TrafficLightStates))
        })
        

        # SUMO Setup
        self._sumo_binary = sumo_binary_path
        self._sumo_config = sumo_config_path
        self._sumo_command = [self._sumo_binary, "-c", self._sumo_config]
        self._max_simulation_seconds = max_simulation_seconds

        # Reset counters
        self._current_time_step = 0
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
        # Close any existing session
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("No simulation running.")
        
        # Start new session
        traci.start(self._sumo_command) # Need to press play in the GUI after this if in GUI mode

        # Reset counters
        self._current_time_step = 0
        self._current_simulation_time = traci.simulation.getTime()
        self._previous_signal = None
        self._total_signal_changes = 0
        self._total_throughput = 0
        self._total_wait_time = 0
        self._total_reward = 0
        self._done = False
        self._history = None

        # Return the first observation
        # Signal state needs to be read from the simulation, but do this for now.
        
        observations = {
            "traffic": np.array([0]*5, dtype='int64'),
            "signals": 0
        }

        return observations

    def step(self, action):
        
        # Step SUMO
        traci.simulationStep()
        # Increment the time step
        self._current_time_step += 1
        self._current_simulation_time = traci.simulation.getTime()

        # Get cars waiting in N/S direction
        cars_waiting_ns = random.randint(0,5)
        # Get cars waiting in E/W direction
        cars_waiting_ew = random.randint(0,5)
        # Get sum of accumulated wait time for all cars waiting in N/S direction
        time_waiting_ns = random.randint(0,5)
        # Get sum of accumulated wait time for all cars waiting in E/W direction
        time_waiting_ew = random.randint(0,5)
        # Get cars that have entered/passed the intersection (throughput)
        throughput = random.randint(0,5)
        # Get traffic light state
        signal_state = random.randint(0,len(TrafficLightStates)-1)

        # New obs
        observations = {
            "traffic": np.array([cars_waiting_ns,cars_waiting_ew,time_waiting_ns,time_waiting_ew,throughput], dtype='int64'),
            "signals": signal_state
        }

        # End after the maximum simulation time steps
        if self._current_simulation_time >= self._max_simulation_seconds:
            done = True
            traci.close()
        else:
            done = False

        # Calculate Reward
        # 10 points for every car that passes the intersection
        # -1 point for every car waiting at the intersection
        # This will likely be a separate class method in the actual implementation
        throughput_reward = throughput * 10
        waiting_punishment = cars_waiting_ns + cars_waiting_ew
        reward = throughput_reward - waiting_punishment

        # Optionally we can pass additional info, we are not using that for now
        info = {"simulation_time":self._current_simulation_time}

        ## Update values
        # Update total signal changes
        if TrafficLightStates(action).name != self._previous_signal:
            self._total_signal_changes += 1
        self._previous_signal = TrafficLightStates(action).name

        # Update total throughput
        self._total_throughput += throughput
        # Update total wait time
        self._total_wait_time += (time_waiting_ns + time_waiting_ew)
        # Update total reward
        self._total_reward += reward

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
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            print("No simulation running.")

# Define environment
env = SimplestIntersection(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="_sumo\\simplest_intersection.sumocfg",
    max_simulation_seconds=3600
)
# If the environment don't follow the interface, an error will be thrown
check_env(env, warn=True)

# Dummy loop of random actions
env.reset()
done = False
step = 0
while not done:
  #action, _ = model.predict(obs, deterministic=True)
  step += 1
  action = env.action_space.sample()
  print("Step {}".format(step))
  print("Action: ", TrafficLightStates(action).name)
  obs, reward, done, info = env.step(action)
  print('obs=', obs, 'reward=', reward, 'done=', done, "info=", info)
  env.render(mode='console')
  if done:
    # Note that the VecEnv resets automatically
    # when a done signal is encountered
    print("Goal reached!", "reward=", reward)
    break