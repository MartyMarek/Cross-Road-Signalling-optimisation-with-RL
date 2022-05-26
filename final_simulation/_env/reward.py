

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
