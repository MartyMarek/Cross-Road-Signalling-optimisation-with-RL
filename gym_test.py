import gym
from stable_baselines3.common.env_checker import check_env
from _env.simplest_intersection import SimplestIntersection
from _sumo.simplest_intersection_simulation import SignalStates, SumoSimulation

# Define simulation
simulation = SumoSimulation(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="_sumo\\_config\\simplest_intersection.sumocfg",
    signal_states=SignalStates
)

# Define environment
env = SimplestIntersection(
    simulation=simulation,
    max_simulation_seconds=3600
)

# Validate the environment
#check_env(env, warn=True)

# Test the environment
env.reset()
done = False
step = 1
while not done:
  #action, _ = model.predict(obs, deterministic=True)
  step += 1
  action = env.action_space.sample()
  print("Step {}".format(step))
  print("Action: ", SignalStates(action).name)
  obs, reward, done, info = env.step(action)
  print('obs=', obs, 'reward=', reward, 'done=', done, "info=", info)
  env.render(mode='console')
  if done:
    # Note that the VecEnv resets automatically
    # when a done signal is encountered
    print("Goal reached!", "reward=", env._total_reward)
    break

#endregion