import pandas as pd
import traci

class Category:


    def __init__(self):
        # we return a list of dataframes
        categories = []


    def categorise(self, data):

        # get vehicles travelling horizontally and vertically
        horizontal = data[data['vehicle_id'].str.contains('south|north')]
        vertical = data[data['vehicle_id'].str.contains('east|west')]

        # get the total wait time for all vehicles
        hTotalTime = horizontal['accumulated_waiting_time'].sum()
        vTotalTime = vertical['accumulated_waiting_time'].sum()

        return horizontal, vertical, hTotalTime, vTotalTime


