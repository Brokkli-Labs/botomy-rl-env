import gymnasium as gym
from stable_baselines3 import PPO
from env import CustomEnv

# Create the custom environment
env = CustomEnv()

# Instantiate the agent
model = PPO("MlpPolicy", env, verbose=1)

# Train the agent
model.learn(total_timesteps=10000)

# Save the agent
model.save("ppo_custom_env")

# Load the trained agent
model = PPO.load("ppo_custom_env")

# Evaluate the agent
obs = env.reset()
for _ in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    if dones:
        obs = env.reset()
