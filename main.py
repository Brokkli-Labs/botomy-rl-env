from datetime import datetime
from pathlib import Path
import gymnasium as gym
from gymnasium.wrappers import TimeLimit

from env import CustomEnv

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
import argparse

from hyper_parameter_callback import HyperParamCallback

env = gym.make('CustomEnv-v0')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--n_steps", type=int, default=1000)
    parser.add_argument("--n_epochs", type=int, default=2)
    parser.add_argument("--total_timesteps", type=int, default=100000)
    parser.add_argument("--checkpoint_freq", type=int, default=1000)
    parser.add_argument("--max_episode_steps", type=int, default=250)
    parser.add_argument("--train", type=bool, default=False)
    parser.add_argument("--log_path", type=str, default="./logs")
    parser.add_argument("--checkpoint_path", type=str, default="./checkpoints")
    parser.add_argument("--model_path", type=str, default="model.zip")

    args = parser.parse_args()

    # hyperparameters
    n_steps = args.n_steps
    n_epochs = args.n_epochs
    batch_size = args.n_steps
    total_timesteps = args.total_timesteps

    # env
    max_episode_steps = args.max_episode_steps

    # mode
    train = args.train
    checkpoint_freq = args.checkpoint_freq

    # paths
    log_path = args.log_path
    checkpoint_path = args.checkpoint_path
    model_path = args.model_path

    env = TimeLimit(env, max_episode_steps=max_episode_steps)

    if train:
        print("Training model")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        run_name = f"train-{timestamp}"

        model = PPO("MlpPolicy", env, n_steps=n_steps, n_epochs=n_epochs, batch_size=batch_size, tensorboard_log=log_path)


        # save model checkpoints
        # https://stable-baselines3.readthedocs.io/en/master/guide/callbacks.html#stoptrainingcallback
        checkpoint_callback = CheckpointCallback(
            save_freq=checkpoint_freq,
            save_path=checkpoint_path,
            name_prefix="rl_model",
            save_replay_buffer=True,
            save_vecnormalize=True,
        )
        hyperparam_callback = HyperParamCallback()
        callback = CallbackList([checkpoint_callback, hyperparam_callback])

        # add a progress bar so you know it's not frozen
        model.learn(total_timesteps=total_timesteps, progress_bar=True, callback=callback, tb_log_name=run_name)
        model.save("rpg_agent")
    else:
        print("Inference mode")

        model_path = Path(model_path)
        if not model_path.exists():
            print("no model found")
        else:
            model = PPO.load("rpg_agent", env, n_steps=n_steps, n_epochs=n_epochs, batch_size=batch_size)

            env = model.get_env()
            obs = env.reset()
            for i in range(total_timesteps):
                action, _state = model.predict(obs, deterministic=True)
                obs, reward, done, info = env.step(action)
