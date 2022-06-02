import numpy as np
import os
import random
import pandas as pd


class SARSA():

    def __init__(self,
        n_episodes,
        epsilon_initial,
        epsilon_decay_episodes_percent,
        alpha,
        gamma,
        discrete_observation_bins,
        env,
        log_dir,
        epsilon_final = 0
    ):

        self._n_episodes = n_episodes
        self._current_episode = 0
        self._epsilon_initial = epsilon_initial
        self._epsilon_final = epsilon_final
        self._epsilon = self._epsilon_initial
        self._epsilon_decay_episodes_percent = epsilon_decay_episodes_percent
        self._begin_epsilon_decay_episode = 1
        self._final_epsilon_decay_episode = np.ceil(self._n_episodes * self._epsilon_decay_episodes_percent)
        self._epsilon_decay_value = (self._epsilon_initial - self._epsilon_final) / (self._final_epsilon_decay_episode - self._begin_epsilon_decay_episode)
        self._alpha = alpha
        self._gamma = gamma
        self._discrete_observation_bins = discrete_observation_bins
        self._env = env
        self._log_dir = log_dir
        self._q_table = np.random.uniform(low=-2, high=0, size=([len(obs_bin) for obs_bin in self._discrete_observation_bins] + [self._env.action_space.n]))
        self._rewards = list()
        self._episodes = list()
        self._epsilons = list()
        self._total_throughput = list()

    def discretise_observation(self,observation):

        discrete_observation = list()

        for i in range(len(observation)):
            discrete_observation.append(np.digitize(observation[i], self._discrete_observation_bins[i]) - 1) # -1 will turn bin into index
        
        return tuple(discrete_observation)

    def choose_action(self,observation):

        action=0
        
        if np.random.uniform(0, 1) < self._epsilon:
            action = self._env.action_space.sample()
        else:
            #action = np.argmax(self._q_table[observation, :])
            action = np.argmax(self._q_table[observation])

        return action

    def decay_epsilon(self):

        if self._final_epsilon_decay_episode > self._current_episode and self._current_episode >= self._begin_epsilon_decay_episode:
            self._epsilon -= self._epsilon_decay_value
        
        self._epsilons.append(self._epsilon)

    def learn(self):
        
        self.save_monitor_full()

        while self._current_episode < self._n_episodes:
            
            print("Episode: ", self._current_episode + 1)

            total_reward = 0
            done = False
            current_obs = self.discretise_observation(observation=self._env.reset())
            current_action = self.choose_action(observation=current_obs)
            self.decay_epsilon()
            #print("Epsilon: ", self._epsilon)

            while done != True:

                raw_next_obs, reward, done, info = self._env.step(action=current_action)
                next_obs = self.discretise_observation(observation=raw_next_obs)
                next_action = self.choose_action(observation=next_obs)

                self._q_table[current_obs][current_action] = self._q_table[current_obs][current_action] + self._alpha * (reward + self._gamma * self._q_table[next_obs][next_action] - self._q_table[current_obs][current_action])

                current_obs = next_obs
                current_action = next_action
                total_reward += reward

            self._current_episode += 1
            self._rewards.append(total_reward)
            self._episodes.append(self._current_episode)
            self._total_throughput.append(self._env._total_throughput)

            self.save_monitor_incremental()

        self.save_monitor_full()
        self.save_q_table()

    def save_monitor_incremental(self):

        output_path = "{0}\\monitor.csv".format(self._log_dir)

        data = dict(
            episode = [self._episodes[-1]],
            reward = [self._rewards[-1]],
            total_throughput = [self._total_throughput[-1]],
            epsilon = [self._epsilons[-1]]
        )

        incremental_monitor_df = pd.DataFrame(data=data)
        incremental_monitor_df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

    def save_monitor_full(self):

        output_path = "{0}\\monitor.csv".format(self._log_dir)

        data = dict(
            episode = self._episodes,
            reward = self._rewards,
            total_throughput = self._total_throughput,
            epsilon = self._epsilons
        )

        complete_monitor_df = pd.DataFrame(data=data)
        complete_monitor_df.to_csv(output_path, mode='w',index=False)

    def save_q_table(self):

        np.save("{0}\\final_q_table".format(self._log_dir),self._q_table)

