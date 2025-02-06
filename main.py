from pathlib import Path
import gymnasium as gym
from stable_baselines3 import PPO

env = gym.make('CustomEnv-v0')
if __name__ == "__main__":
    # Train PPO agent
    model_path = Path("rpg_agent.zip")
    if model_path.exists():
      model = PPO.load("rpg_agent", env, verbose=2)
    else:
      print("no model found")
      model = PPO("MlpPolicy", env, verbose=2)
    
    total_timesteps=5000000
    checkpoint_freq = 50000  # Save every 50,000 timesteps
    for i in range(0, total_timesteps, checkpoint_freq):
        model.learn(total_timesteps=checkpoint_freq)
        model.save("rpg_agent")  
    