import random
import gym
import numpy as np
import pandas as pd
import os

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
    max_simulation_seconds=120
)


# creating the hyperparameters

alpha = 0.1
discount = 0.9
epsilon = 1
max_epsilon = 1
min_epsilon = 0.01
decay = 0.001

train_episodes = 2000
test_episodes = 100
max_steps = 100

# create the Q-Table
q_table = np.random.uniform(low=-2, high=0, size=([4,4,8,8,4] + [env.actions.n]))

rewards = []
epsilons = []
throughputs = []


for episode in range(train_episodes):

    currentState = env.reset()
    total_rewards  = 0
    total_throughput = 0

    print("Training episode:", episode)

    for step in range(120):
        # generate random number between 0 and 1
        nextStep = random.uniform(0, 1)

        # as epsilon decreases, the random number between 0 and 1 will more likely to
        # choose explotation rather than exploration
        if nextStep <= epsilon:
            # exploration path - take a random action
            nextAction = env.actions.sample()
        else:
            # explotation path - take the best step
            nextAction = np.argmax(q_table[currentState])


        # take the action and receive the reward
        nextState, reward, done, info = env.step(nextAction)


        # update Q table
        q_table[currentState][nextAction] = q_table[currentState][nextAction] + \
                                            alpha * (reward + discount * np.max(q_table[nextState]) - \
                                            q_table[currentState][nextAction])

        total_rewards += reward
        total_throughput += info["throughput"]
        currentState = nextState

        # if the episode is finished
        if done == True:
            print("Total reward {}: {}, Epsilon: {}".format(episode, total_rewards, epsilon))
            break


    # reduce the epsilon after each episode to reduce exploration and move towards explotation
    epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay * episode)
    # keep a record of rewards and epsilons
    rewards.append(total_rewards)
    epsilons.append(epsilon)
    throughputs.append(total_throughput)

    #print("Reward: {}, Next Epsilon: {}".format(total_rewards, epsilon))


# once all episodes are done
epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay * episode)
rewards.append(total_rewards)
epsilons.append(epsilon)
throughputs.append(total_throughput)

print("Average Score for this run: " + str(sum(rewards)/train_episodes))

saveData = {'Rewards':rewards, 'Epsilon':epsilons, 'Throughput':throughputs}
df = pd.DataFrame(saveData)

df.to_csv("rewards-epsilons.csv")

log_dir = "_models\\reward_13\\q-learn"
os.makedirs(log_dir, exist_ok=True)

#np.save("\\qlearn_tables\\", q_table)

np.save("{0}\\final_q_table".format(log_dir), q_table)