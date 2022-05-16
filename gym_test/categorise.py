import pandas as pd
import traci

class Category:


    def __init__(self):
        # we return a list of dataframes
        categories = []


    def categorise(self, data):

        horizontal = data[data['vehicle_id'].str.contains('south|north')]
        vertical = data[data['vehicle_id'].str.contains('east|west')]

        return horizontal, vertical


