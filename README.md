# COSC2673 - Computational Machine Learning
# Assignment 2 Repository

This repository contains the simulation setup and reinforcement learning code for the traffic simulation (Q3). 

For setup to work, the following steps are required:

# 1. Installation of the Sumo environment 
The installation can be found at: https://www.eclipse.org/sumo/

# 2. Required libraries to work with python

We used OpenAI gym framework to to manage and interact with our sumo simulation environment. 

We used stable baselines3 which is a set of libraries of various reinforcement learning algorithms using PyTorch.
Stable-Baselines3 requires python 3.7+ and PyTorch >= 1.11

To install these libraries, the following commands can be used from the python terminal:

pip install torch

pip install gym 

followed by 

pip install stable-baselines3

# 3. Setup of simulation files

The SUMO simulatiom configuration files located in the github folder at final_simulation_sumo_files, need to be copied to the local desktop into the C:\sumoconfig\ directory. Without these files the simulation will not be able to run.

# 4. Training models

To execute a training run, select the python notebook file corresponding to the model you want to run. Please note these have already been run and have saved the results. 

* Q-Learning : model_training_qlearn.ipynb
* Sarsa : model_training_qlearn.ipynb
* A2C : model_training_a2c.ipynb
* DQN : model_training_dqn.ipynb
* PPO : model_training_ppo.ipynb

The hyperparameters can be turned in each of these files by providing the desired value to the listed variables in the notebook.

For evaluation of each model (using the best of each model we have created using the training above), you can simply run the following notebook:

* model_evaluation.ipynb

To generate plots to compare each model's metrics, run the following notebook:

* model_evaluation_plots.ipynb

