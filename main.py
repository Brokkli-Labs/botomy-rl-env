from pathlib import Path
import gymnasium as gym
from env import CustomEnv
from stable_baselines3 import PPO
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
import argparse

from hyper_parameter_callback import HyperParamCallback

env = gym.make('CustomEnv-v0')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--n_steps", type=int, default=1000)
    parser.add_argument("--n_epochs", type=int, default=10)
    parser.add_argument("--checkpoint_freq", type=int, default=1000)
    parser.add_argument("--train", type=bool, default=False)
    parser.add_argument("--log_path", type=str, default="./logs")
    parser.add_argument("--checkpoint_path", type=str, default="./checkpoints")
    parser.add_argument("--model_path", type=str, default="model.zip")

    args = parser.parse_args()

    # hyperparameters
    n_steps = args.n_steps
    n_epochs = args.n_epochs
    batch_size = args.n_steps
    total_timesteps = args.n_steps * args.n_epochs

    # mode
    train = args.train
    checkpoint_freq = args.checkpoint_freq

    # paths
    log_path = args.log_path
    checkpoint_path = args.checkpoint_path
    model_path = args.model_path

    # log training data to stdout
    # typically logs at the end of each epoch
    logger = configure(log_path, ["stdout", "tensorboard"])

    if train:
        print("Training model")
        model = PPO("MlpPolicy", env, n_steps=n_steps, n_epochs=n_epochs, batch_size=batch_size)


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

        model.set_logger(logger)

        # add a progress bar so you know it's not frozen
        model.learn(total_timesteps=total_timesteps, progress_bar=True, callback=callback)
        model.save("rpg_agent")
    else:
        print("Inference mode")

        model_path = Path(model_path)
        if not model_path.exists():
            print("no model found")
        else:
            model = PPO.load("rpg_agent", env, n_steps=n_steps, n_epochs=n_epochs, batch_size=batch_size)

            model.set_logger(logger)

            env = model.get_env()
            obs = env.reset()
            for i in range(total_timesteps):
                action, _state = model.predict(obs, deterministic=True)
                obs, reward, done, info = env.step(action)
