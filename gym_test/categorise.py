import pandas as pd
import traci

class Category:


    def __init__(self):
        # we return a list of dataframes
        categories = []


    def categorise(self, data):

        # get vehicles travelling horizontally and vertically
        horizontalList = data[data['vehicle_id'].str.contains('south|north')]
        verticalList = data[data['vehicle_id'].str.contains('east|west')]

        horizontal = len(horizontalList.index)
        vertical = len(verticalList.index)

        # get the total wait time for all vehicles
        hTotalTime = horizontalList['accumulated_waiting_time'].sum()
        vTotalTime = verticalList['accumulated_waiting_time'].sum()

        return horizontal, vertical, hTotalTime, vTotalTime


    def convertLightStateToInt(self, lightState):
        if lightState == 'GGrrGGrr':
            return 0
        if lightState == 'yyrryyrr':
            return 1
        if lightState == 'rrGGrrGG':
            return 2
        if lightState == 'rryyrryy':
            return 3


    def convertLightStateToString(self, lightState):
        if lightState == 0:
            return 'GGrrGGrr'
        if lightState == 1:
            return 'yyrryyrr'
        if lightState == 2:
            return 'rrGGrrGG'
        if lightState == 3:
            return 'rryyrryy'
