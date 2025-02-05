import gymnasium as gym
from env import CustomEnv
import logging
import os
import random

# Clear terminal (Mac/Linux)
os.system('clear')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Create logger
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    env = gym.make('CustomEnv-v0')
    state = env.reset(seed=10, options={
        "round_length": 10,
    })

    episode_over = False
    while not episode_over:
        action = random.randint(0, 4)  # Generate a random action from 0 to 4
        observation, reward, terminated, truncated, info = env.step(action)

        episode_over = terminated or truncated

    env.close()