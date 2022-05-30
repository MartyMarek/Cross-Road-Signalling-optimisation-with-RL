import numpy as np
from final_simulation._env.real_intersection import RealIntersectionSimpleObs12
from final_simulation._sumo.simplest_intersection_simulation import SignalStates, SumoSimulationSimpleObs
import os
import random


stopped_cars_bins = np.array([0,4,10,20,np.inf])
throughput_bins = np.array([0,2,6,12,np.inf])
signals_bins = np.arange(0,8)
signal_timer_bins = np.array([0,5,15,25,np.inf])

bins = [
    # Stopped cars from each cardinal direction
    stopped_cars_bins,
    stopped_cars_bins,
    stopped_cars_bins,
    stopped_cars_bins,
    # Throughput
    throughput_bins,
    # Current signal state
    signals_bins,
    # Previous signal state
    signals_bins,
    # Previous signal active time
    signal_timer_bins
]

def discretise_observations(observations,bins):

    discrete_observations = list()

    for i in range(len(observations)):
        discrete_observations.append(np.digitize(observations[i], bins[i]) - 1) # -1 will turn bin into index
    return tuple(discrete_observations)

def choose_action(Q,state,epsilon):
    action=0
    if np.random.uniform(0, 1) < epsilon:
        action = env.action_space.sample()
    else:
        action = np.argmax(Q[state, :])
    return action


# Sim time 1 minute
max_simulation_seconds = 180
number_episodes = 500

# Define simulation
simulation = SumoSimulationSimpleObs(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)

# Define environment
env = RealIntersectionSimpleObs12(
    simulation=simulation,
    max_simulation_seconds=max_simulation_seconds
)
env.action_space
# Initialize Q table randomly
q_table = np.random.uniform(low=-2, high=0, size=([len(bin) for bin in bins] + [env.action_space.n]))

obs1 = env.reset()

n_episodes = 10
alpha = 0.1
gamma = 0.95

for episode in range(n_episodes):

    current_obs = env.reset()
    if random.uniform(0,1) <= epsilon:
        current_action = env.action_space.sample()
    else:
        current_action = np.argmax(q_table[current_obs,:])
    total_rewards  = 0
    done = False
    print("Training episode:", episode)

    while not done:

        next_obs, reward, done, info = env.step(action=current_action)

        if random.uniform(0,1) <= epsilon:
            next_action = env.action_space.sample()
        else:
            next_action = np.argmax(q_table[next_obs,:])

        q_table[current_obs, current_action] = q_table[current_obs, current_action] + alpha * (reward + gamma * q_table[next_obs, next_action] - q_table[current_obs, current_action])
  
        current_obs = next_obs
        current_action = next_action
          
        #Updating the respective vaLues
        t += 1
        reward += 1
          
        #If at the end of learning process
        if done:
            env.render(mode='console')






EPISODES = 50000

# parameters for epsilon decay policy
EPSILON = 1 # not a constant, going to be decayed
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES // 2
epsilon_decay_value = EPSILON / (END_EPSILON_DECAYING - START_EPSILON_DECAYING)

#for testing
N_TEST_RUNS = 100
TEST_INTERVAL = 5000

