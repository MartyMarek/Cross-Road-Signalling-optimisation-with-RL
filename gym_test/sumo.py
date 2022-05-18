import statespace as state

stateSpace = state.StateSpace("C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui")

stateSpace.beginSimulation()

for _ in range(1000):
    horizontal, vertical, hTime, vTime, lightState, throughput = stateSpace.getCurrentStateSpace()

    print(throughput)

stateSpace.endSimulation()
