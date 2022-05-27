#import gym
from stable_baselines3.common.env_checker import check_env
from final_simulation._env.simplest_intersection import SimplestIntersection
from final_simulation._sumo.simplest_intersection_simulation import SignalStates, SumoSimulation
from stable_baselines3 import PPO, DQN, A2C, DDPG
from stable_baselines3.common.evaluation import evaluate_policy

# Define simulation
simulation = SumoSimulation(
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)

# Define environment
train_env = SimplestIntersection(
    simulation=simulation,
    max_simulation_seconds=900
)

# train_env = SimplestIntersection(
#     simulation=simulation,
#     max_simulation_seconds=100
# )
SignalStates(0).name.replace('r','')[0] == 'g'

#region Train model
model = PPO('MultiInputPolicy',train_env,learning_rate=0.001,verbose=1)
model = A2C.load("model_a2c_tts_90000_lr_1e-3_reward_02a.zip")
model.learn(total_timesteps=3600)
mean_reward, std_reward = evaluate_policy(model, train_env, n_eval_episodes=2, deterministic=True,)
evalu = evaluate_policy(model, train_env, n_eval_episodes=2, deterministic=True, return_episode_rewards= True)
model = DQN('MultiInputPolicy',train_env,learning_rate=0.001,verbose=1)
model.learn(total_timesteps=3600)
#model = PPO('MultiInputPolicy', train_env, learning_rate=1e-3,verbose=0,device='cuda')
model = DDPG('MultiInputPolicy', train_env, learning_rate=0.001,verbose=0,device='auto')
model.learn(n_eval_episodes=10)
#model.save("model_ppo_tts_3600_lr_1e-3_reward_02")
model.save("model_ddpg_tts_9000_lr_1e-3_reward_02a")
#model = model.load("a2c_testing")

#endregion

#region Test model

validation_simulation = SumoSimulation(
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="_sumo\\_config\\simplest_intersection.sumocfg",
    signal_states=SignalStates
)

validation_env = SimplestIntersection2(
    simulation=validation_simulation,
    max_simulation_seconds=900
)
observation = validation_env.reset()

while True:
    #observation = observation[np.newaxis, ...]

    # action = env.action_space.sample()
    action, _states = model.predict(observation)
    observation, reward, done, info = validation_env.step(float(action))

    # env.render()
    if done:
        print("info:", info)
        validation_env.render()
        break

#endregion

#region Test the environment
simulation.beginSimulation()

test_env = SimplestIntersection(
    simulation=simulation,
    max_simulation_seconds=900
)
# Validate the environment
check_env(test_env, warn=True)

observation = validation_env.reset()

test_env.reset()
done = False
step = 1
while not done:
  #action, _ = model.predict(obs, deterministic=True)
  step += 1
  action = test_env.action_space.sample()
  #print("Step {}".format(step))
  #print("Action: ", SignalStates(action).name)
  obs, reward, done, info = test_env.step(action)
  #print('obs=', obs, 'reward=', reward, 'done=', done, "info=", info)
  if step % 100 == 0:
    print(info)
    test_env.render(mode='console')
  if done:
    # Note that the VecEnv resets automatically
    # when a done signal is encountered
    print("Goal reached!", "reward=", test_env._total_reward)
    break


#endregion