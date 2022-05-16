import pygame
import math
import os, sys
import pandas as pd
import traci


class CrossingGame:

    def __init__(self):
        # Running Sumo
        sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo', 'tools'))
        sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"

        # File to run
        sumoCmd = [sumoBinary, "-c", "_sumo\\simplest_intersection.sumocfg"]

        # used to set the display to automatic
        pd.options.display.width = 0

        traci.start(sumoCmd)  # Need to press play in the GUI after this


    def action(self, action):

        # only two actions exists at the moment
        # set the horizontal lanes to green
        if action == 0:
            return

        if action == 1:
            return


    def evaluate(self):
        reward = 0

        #set the reward and return it
        return reward


    def observe(self):
        # return the state
        return [0,0]