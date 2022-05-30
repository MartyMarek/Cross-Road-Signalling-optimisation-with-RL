
import numpy as np

def qlearning_reward_01(observation):
    hVehiclesWaiting = observation[0]
    hRightVehiclesWaiting = observation[1]
    vVehiclesWaiting = observation[2]
    vRightVehiclesWaiting = observation[3]
    hTotalTime = observation[4]
    hRightTotalTime = observation[5]
    vTotalTime = observation[6]
    vRightTotalTime = observation[7]
    throughput = observation[8]
    lightState = observation[9]

    throughputRatio = throughput - hVehiclesWaiting - hRightVehiclesWaiting - vVehiclesWaiting - vRightVehiclesWaiting

    if  throughputRatio < 0:
        return abs(1/throughputRatio)
    else:
        return throughputRatio

def qlearning_reward_02(observation):
    hVehiclesWaiting = observation[0]
    hRightVehiclesWaiting = observation[1]
    vVehiclesWaiting = observation[2]
    vRightVehiclesWaiting = observation[3]
    hTotalTime = observation[4]
    hRightTotalTime = observation[5]
    vTotalTime = observation[6]
    vRightTotalTime = observation[7]
    throughput = observation[8]
    lightState = observation[9]

    totalWaitTime = hTotalTime + hRightTotalTime + vTotalTime + vRightTotalTime

    if totalWaitTime == 0:
        return 1
    else:
        return 1 / totalWaitTime

def qlearning_reward_03(observation):
    hVehiclesWaiting = observation[0]
    hRightVehiclesWaiting = observation[1]
    vVehiclesWaiting = observation[2]
    vRightVehiclesWaiting = observation[3]
    hTotalTime = observation[4]
    hRightTotalTime = observation[5]
    vTotalTime = observation[6]
    vRightTotalTime = observation[7]
    throughput = observation[8]
    lightState = observation[9]

    totalWaitTime = hTotalTime + hRightTotalTime + vTotalTime + vRightTotalTime

    throughputReward = throughput / 10

    if totalWaitTime == 0:
        return 1 + throughputReward
    else:
        return (1 / totalWaitTime) + throughputReward



def qlearning_reward_04(observation):
    hVehiclesWaiting = observation[0]
    hRightVehiclesWaiting = observation[1]
    vVehiclesWaiting = observation[2]
    vRightVehiclesWaiting = observation[3]
    hTotalTime = observation[4]
    hRightTotalTime = observation[5]
    vTotalTime = observation[6]
    vRightTotalTime = observation[7]
    throughput = observation[8]
    lightState = observation[9]
    lightStatusTime = observation[10]

    reward = 0

    # we don't want the lights to be orange for too long
    if lightState == 1 or lightState == 3 or lightState == 5 or lightState == 7:
        if lightStatusTime >= 1:
            reward = reward - 5

    # if the horizontal lights are green..
    if lightState == 6:
        reward = reward + (hVehiclesWaiting - hRightTotalTime - vTotalTime - vRightTotalTime)

    # if vertical lights are green
    if lightState == 2:
        reward = reward + (vVehiclesWaiting - vRightTotalTime - hTotalTime - hRightTotalTime)

    # if horizontal right turn lights are green
    if lightState == 4:
        reward = reward + hRightVehiclesWaiting - hTotalTime - vTotalTime - vRightTotalTime

    # if vertical right turn lights are green
    if lightState == 0:
        reward = reward + vRightVehiclesWaiting - vTotalTime - hTotalTime - hRightTotalTime

    reward = reward + throughput

    return reward



def calculate_reward_01(throughput):
    reward = float(throughput * 10)

    return reward


def calculate_reward_02(throughput, cars_waiting, current_signal_state, previous_signal_state,
                        previous_signal_active_time):

    throughput_reward = throughput * 10
    waiting_punishment = cars_waiting * 2

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 50
    else:
        short_signal_punishment = 0

    reward = throughput_reward - waiting_punishment - short_signal_punishment

    return reward


def calculate_reward_03(observations):

    # add up all of the stopped cars
    stopped_vehicles = observations['traffic'][1] + observations['traffic'][6] + \
                        observations['traffic'][11] + observations['traffic'][16]

    # return the highest award for no stopped cars
    if stopped_vehicles == 0:
        return 1

    # higher stopped cars mean lower reward returned
    return 1 / stopped_vehicles


def calculate_reward_04(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):

    throughput_reward = throughput * 3
    waiting_cars_punishment = cars_waiting

    if cars_waiting > 0:
        average_wait_time = accumulated_wait_time/cars_waiting
    else:
        average_wait_time = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 5
    else:
        short_signal_punishment = 0

    reward = throughput_reward - waiting_cars_punishment - average_wait_time - short_signal_punishment

    return reward

def calculate_reward_05(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):


    if cars_waiting > 0:
        average_wait_time = accumulated_wait_time/cars_waiting
    else:
        average_wait_time = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 2
    else:
        short_signal_punishment = 0

    if cars_waiting > 0:
        throughput_reward = throughput/cars_waiting
    else:
        throughput_reward = throughput

    reward = throughput_reward - short_signal_punishment

    return reward

def calculate_reward_06(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):


    if cars_waiting > 0:
        average_wait_time = accumulated_wait_time/cars_waiting
    else:
        average_wait_time = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 2
    else:
        short_signal_punishment = 0

    if current_signal_state == previous_signal_state and previous_signal_active_time > 20:
        long_signal_punishment = 2
    else:
        long_signal_punishment = 0

    if cars_waiting > 0:
        throughput_reward = throughput/cars_waiting
    else:
        throughput_reward = throughput

    reward = throughput_reward - short_signal_punishment - long_signal_punishment

    return reward

def calculate_reward_07(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):


    if cars_waiting > 0:
        average_wait_time = accumulated_wait_time/cars_waiting
    else:
        average_wait_time = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 2
    else:
        short_signal_punishment = 0

    if current_signal_state == previous_signal_state and previous_signal_active_time > 20:
        long_signal_punishment = 2
    else:
        long_signal_punishment = 0

    throughput_reward = throughput * 5

    reward = throughput_reward - average_wait_time - short_signal_punishment - long_signal_punishment

    return reward

def calculate_reward_08(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):


    if cars_waiting > 0:
        average_wait_time_punishment = (accumulated_wait_time/cars_waiting) * 0.5
    else:
        average_wait_time_punishment = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 20
    else:
        short_signal_punishment = 0

    if current_signal_state == previous_signal_state and previous_signal_active_time > 20:
        long_signal_punishment = 2
    else:
        long_signal_punishment = 0

    throughput_reward = throughput * 10

    reward = throughput_reward - average_wait_time_punishment - short_signal_punishment - long_signal_punishment

    return reward


def calculate_reward_09(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):

    if cars_waiting > 0:
        average_wait_time_punishment = (accumulated_wait_time/cars_waiting) * 0.5
    else:
        average_wait_time_punishment = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 20
    else:
        short_signal_punishment = 0

    if current_signal_state == previous_signal_state and previous_signal_active_time > 25:
        long_signal_punishment = 20
    else:
        long_signal_punishment = 0

    throughput_reward = throughput * 5
    cars_waiting_punishment = cars_waiting

    reward = throughput_reward - cars_waiting_punishment - short_signal_punishment - long_signal_punishment

    return reward

def calculate_reward_10(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time):

    if cars_waiting > 0:
        average_wait_time_punishment = (accumulated_wait_time/cars_waiting) * 0.5
    else:
        average_wait_time_punishment = 0

    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 30
    else:
        short_signal_punishment = 0

    if current_signal_state == previous_signal_state and previous_signal_active_time > 30:
        long_signal_punishment = 20
    else:
        long_signal_punishment = 0

    throughput_reward = throughput * 6
    cars_waiting_punishment = cars_waiting

    reward = throughput_reward - cars_waiting_punishment - short_signal_punishment - long_signal_punishment

    return reward

def calculate_reward_11(throughput, cars_waiting, accumulated_wait_time, current_signal_state, previous_signal_state,
                        previous_signal_active_time, signal_states):

    # Cars waiting punishment
    cars_waiting_punishment = cars_waiting

    # Average wait time punishment
    if cars_waiting > 0:
        average_wait_time_punishment = accumulated_wait_time/cars_waiting
    else:
        average_wait_time_punishment = 0

    # Accumulated wait time punishment
    accumulated_wait_time_punishment = accumulated_wait_time

    # Short signal punishment
    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 60
    else:
        short_signal_punishment = 0

    # Long signal punishment
    if current_signal_state == previous_signal_state and previous_signal_active_time > 30:
        long_signal_punishment = 20
    else:
        long_signal_punishment = 0

    # Correct sequence reward
    if signal_states(previous_signal_state).name == 'rgrrrgrr' and signal_states(current_signal_state).name == 'ryrrryrr':
        signal_sequence_reward = 40
    elif signal_states(previous_signal_state).name == 'GrrrGrrr' and signal_states(current_signal_state).name == 'yrrryrrr':
        signal_sequence_reward = 40
    elif signal_states(previous_signal_state).name == 'rrrgrrrg' and signal_states(current_signal_state).name == 'rrryrrry':
        signal_sequence_reward = 40
    elif signal_states(previous_signal_state).name == 'rrGrrrGr' and signal_states(current_signal_state).name == 'rryrrryr':
        signal_sequence_reward = 40
    else:
        signal_sequence_reward = 0

    # Throughput reward
    throughput_reward = throughput * 10
    

    reward = throughput_reward + signal_sequence_reward - accumulated_wait_time_punishment - cars_waiting_punishment - short_signal_punishment - long_signal_punishment

    return reward


def calculate_reward_12(throughput, cars_waiting, current_signal_state, previous_signal_state,
                        previous_signal_active_time, signal_states):

    # Cars waiting punishment
    cars_waiting_punishment = cars_waiting

    # Short signal punishment
    if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
        short_signal_punishment = 60
    else:
        short_signal_punishment = 0

    # Long signal punishment
    if current_signal_state == previous_signal_state and previous_signal_active_time > 30:
        long_signal_punishment = 20
    else:
        long_signal_punishment = 0

    # Correct sequence reward
    if signal_states(previous_signal_state).name == 'rgrrrgrr' and signal_states(current_signal_state).name == 'ryrrryrr':
        signal_sequence_reward = 40
    elif signal_states(previous_signal_state).name == 'GrrrGrrr' and signal_states(current_signal_state).name == 'yrrryrrr':
        signal_sequence_reward = 40
    elif signal_states(previous_signal_state).name == 'rrrgrrrg' and signal_states(current_signal_state).name == 'rrryrrry':
        signal_sequence_reward = 40
    elif signal_states(previous_signal_state).name == 'rrGrrrGr' and signal_states(current_signal_state).name == 'rryrrryr':
        signal_sequence_reward = 40
    else:
        signal_sequence_reward = 0

    # Throughput reward
    throughput_reward = throughput * 10
    

    reward = throughput_reward + signal_sequence_reward - cars_waiting_punishment - short_signal_punishment - long_signal_punishment

    return np.float(reward)