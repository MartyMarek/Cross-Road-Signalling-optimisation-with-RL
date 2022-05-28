import random
import gym
import numpy as np
from _env.qlearn_intersection import SimplestIntersection
from _sumo.qlearn_simulation import SignalStates, SumoSimulation


# setup the gym environment using the sumo simulation
simulation = SumoSimulation(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)

env = SimplestIntersection(
    simulation=simulation,
    max_simulation_seconds=180
)


# creating the hyperparameters

alpha = 0.001
discount = 0.9
epsilon = 1
max_epsilon = 1
min_epsilon = 0.01
decay = 0.01

train_episodes = 100
test_episodes = 100
max_steps = 100

# create the Q-Table
q_table = np.zeros((env.observation_space, env.action_space), dtype=int)

rewards = []
epsilons = []

for episode in range(train_episodes):

    currentState = env.reset()
    total_rewards  = 0

    print("Training episode", episode+1)

    for step in range(100):
        # generate random number between 0 and 1
        nextStep = random.uniform(0, 1)

        # as epsilon decreases, the random number between 0 and 1 will more likely to
        # choose explotation rather than exploration
        if nextStep <= epsilon:
            # exploration path - take a random action
            nextAction = env.actions.sample()
        else:
            # explotation path - take the best step
            nextAction = np.argmax(q_table[currentState,:])

        # take the action and receive the reward
        obsState, reward, done = env.step(nextAction)

        nextState = obsState[0] + obsState[1] * 6 + obsState[2] * 6^2 + obsState[3] * 6^3 + obsState[4] * 6^4 + \
                    obsState[5] * 6^5 + obsState[6] * 6^6 + obsState[7] * 6^7 + obsState[8] * 6^8 + \
                    + obsState[9] * 6^8 * 8

        # update Q table
        q_table[currentState, nextAction] = q_table[currentState, nextAction] + \
                                            alpha * (reward + discount * np.max(q_table[nextState, :]) - \
                                            q_table[currentState, nextAction])

        total_rewards += reward
        currentState = nextState

        # if the episode is finished
        if done == True:
            print("Total reward {}: {}".format(episode, total_rewards))
            break


    # reduce the epsilon after each episode to reduce exploration and move towards explotation
    epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay * episode)
    # keep a record of rewards and epsilons
    rewards.append(total_rewards)
    epsilons.append(epsilon)


# once all episodes are done
epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay * episode)
rewards.append(total_rewards)
epsilons.append(epsilon)

print("Average Score for this run: " + str(sum(rewards)/train_episodes))