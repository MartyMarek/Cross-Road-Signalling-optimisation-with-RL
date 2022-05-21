

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



