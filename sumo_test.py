import os, sys


# if 'SUMO_HOME' in os.environ:
#     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#     sys.path.append(tools)
# else:
#     sys.exit("please declare environment variable 'SUMO_HOME'")

sys.path.append(os.path.join('c:', os.sep, 'Program Files (x86)', 'Eclipse', 'Sumo','tools'))

sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui"
sumoCmd = [sumoBinary, "-c", "_sumo\\simplest_intersection.sumocfg"]

import traci
traci.start(sumoCmd)
step = 0
while step < 1000:
   traci.simulationStep()
   step += 1

traci.close()