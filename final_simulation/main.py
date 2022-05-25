from stable_baselines3.common.env_checker import check_env
from final_simulation._env.simplest_intersection import SimplestIntersection, SimplestIntersection
from final_simulation._sumo.simplest_intersection_simulation import SignalStates, SumoSimulation
from stable_baselines3 import A2C, PPO, DQN
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback
import os


#region Test With Wrapper

# Create log dir
log_dir = "final_simulation\\_models\\dqn_rew_04_el_180_lr_0.0001"
os.makedirs(log_dir, exist_ok=True)

# Sim time 1 minute
max_simulation_seconds = 180
number_episodes = 10000

# Define simulation
simulation = SumoSimulation(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)

# Create and wrap the environment
# Define environment
env = SimplestIntersection(
    simulation=simulation,
    max_simulation_seconds=max_simulation_seconds
)
# Logs will be saved in log_dir/monitor.csv
env = Monitor(env, log_dir)

eval_simulation = SumoSimulation(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)
eval_env = SimplestIntersection(
    simulation=eval_simulation,
    max_simulation_seconds=max_simulation_seconds
)
eval_env = Monitor(eval_env, log_dir)


# Create the callback: check every 1000 steps
callback = EvalCallback(eval_env=eval_env,eval_freq=10*max_simulation_seconds,best_model_save_path=log_dir,n_eval_episodes=1,log_path=log_dir)
model = DQN('MultiInputPolicy', env, verbose=0, device='auto', train_freq=(10,'step'), learning_rate=0.0001)
#model = PPO('MultiInputPolicy', env, verbose=0, device='auto', learning_rate=0.0001)
#model = A2C('MultiInputPolicy', env, verbose=0, device='auto', learning_rate=0.1)
# Train the agent
model.learn(total_timesteps=int(max_simulation_seconds*number_episodes), callback=callback)

#endregion

# Define simulation
simulation = SumoSimulation(
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)


# Define environment
train_env = SimplestIntersection(
    simulation=simulation,
    max_simulation_seconds=900
)

#region Train model

model = PPO('MultiInputPolicy', train_env, learning_rate=1e-3,verbose=0,device='cuda')
#model = DDPG('MultiInputPolicy', train_env, learning_rate=0.001,verbose=0,device='auto')
model.learn(n_eval_episodes=10, total_timesteps=360000)
model.save("model_ppo_tts_360000_lr_1e-3_reward_02_final_sim")
#model.save("model_ddpg_tts_9000_lr_1e-3_reward_02a")
#model = model.load("a2c_testing")
#train_env._simulation.endSimulation()
#endregion

#region Test model

validation_simulation = SumoSimulation(
    #sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo",
    sumo_binary_path="C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui",
    sumo_config_path="C:\\sumoconfig\\real_intersection.sumocfg",
    signal_states=SignalStates
)

validation_env = SimplestIntersection(
    simulation=validation_simulation,
    max_simulation_seconds=900
)
observation = validation_env.reset()

model = A2C.load("final_simulation\\_models\\a2c_rew_04\\best_model.zip")

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