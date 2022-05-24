

def calculate_reward_01(throughput):
    reward = float(throughput * 10)

    return reward


def calculate_reward_02(observations):

    # add up all of the stopped cars
    stopped_vehicles = observations['traffic'][1] + observations['traffic'][6] + \
                        observations['traffic'][11] + observations['traffic'][16]

    # return the highest award for no stopped cars
    if stopped_vehicles == 0:
        return 1

    # higher stopped cars mean lower reward returned
    return 1 / stopped_vehicles

def calculate_reward_03(throughput,cars_waiting,current_signal_state,previous_signal_state,previous_signal_active_time):

        throughput_reward = throughput * 10
        waiting_punishment = cars_waiting * 2

        if current_signal_state != previous_signal_state and previous_signal_active_time < 5:
            short_signal_punishment = 50
        else:
            short_signal_punishment = 0

        reward = throughput_reward - waiting_punishment - short_signal_punishment

        return reward



