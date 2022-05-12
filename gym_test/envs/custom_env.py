import gym
from gym import spaces
import numpy as np
from gym_testcross.envs.crossing import CrossingGame

class CustomEnv(gym.Env):

    def __init__(self):
        self.pygame = CrossingGame()

        #either turn horizontal or vertical lights green
        self.action_space = spaces.Discrete(2)

        #observation space - how many cars are banked up horizontally and vertically?
        self.observation_space = spaces.Box(np.array([0,0]), np.array([50, 50]), dtype=np.int)

    def reset(self):
        del self.pygame
        self.pygame = CrossingGame()
        observe = self.pygame.observe()
        return observe

    def step(self, action):
        self.pygame.action(action)
        observe = self.pygame.observe()
        reward = self.pygame.evaluate()
        done = self.pygame.is_done()
        return observe, reward, done, {}

    def render(self, mode="human", close=False):
        self.pygame.view()
