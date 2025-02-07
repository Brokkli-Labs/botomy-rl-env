from pathlib import Path
import gymnasium as gym
from env import CustomEnv
from stable_baselines3 import PPO
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import CheckpointCallback

tmp_path = "/tmp/sb3_log/"
checkpoint_path = "./sb3_checkpoints/"

env = gym.make('CustomEnv-v0')
if __name__ == "__main__":
    # hyperparameters
    n_steps = 1000
    n_epochs = 10
    batch_size = n_steps
    total_timesteps = n_steps * n_epochs
    checkpoint_freq = n_steps

    # Train PPO agent
    model_path = Path("rpg_agent.zip")
    if model_path.exists():
      model = PPO.load("rpg_agent", env, verbose=2, n_steps=n_steps, n_epochs=n_epochs, batch_size=batch_size)
    else:
      print("no model found")
      model = PPO("MlpPolicy", env, verbose=2, n_steps=n_steps, n_epochs=n_epochs, batch_size=batch_size)


    # log training data to stdout
    # typically logs at the end of each epoch
    logger = configure(tmp_path, ["stdout"])

    checkpoint_callback = CheckpointCallback(
        save_freq=checkpoint_freq,
        save_path=checkpoint_path,
        name_prefix="rl_model",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    model.set_logger(logger)

    # add a progress bar so you know it's not forzen
    model.learn(total_timesteps=total_timesteps, progress_bar=True, callback=checkpoint_callback)
    model.save("rpg_agent")
