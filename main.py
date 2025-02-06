import gymnasium as gym
from agent import BotomyAgent
from env import CustomEnv
import random
from tqdm import tqdm

# hyperparameters
learning_rate = 0.01
n_episodes = 100_000
start_epsilon = 1.0
epsilon_decay = start_epsilon / (n_episodes / 2)  # reduce the exploration over time
final_epsilon = 0.1

env = gym.make('CustomEnv-v0')
env = gym.wrappers.RecordEpisodeStatistics(env, buffer_length=n_episodes)

agent = BotomyAgent(
    env=env,
    learning_rate=learning_rate,
    initial_epsilon=start_epsilon,
    epsilon_decay=epsilon_decay,
    final_epsilon=final_epsilon,
)
if __name__ == "__main__":
    for episode in tqdm(range(n_episodes)):
        obs, info = env.reset(seed=10, options={"round_length": 2})
        done = False

        # play one episode
        while not done:
            action = agent.get_action(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)

            # update the agent
            agent.update(obs, action, reward, terminated, next_obs)

            # update if the environment is done and the current obs
            done = terminated or truncated
            obs = next_obs

        agent.decay_epsilon()


    # env = gym.make('CustomEnv-v0')
    # state = env.reset(seed=10, options={
    #     "round_length": 10,
    # })

    # episode_over = False
    # while not episode_over:
    #     action = random.randint(0, 4)  # Generate a random action from 0 to 4
    #     observation, reward, terminated, truncated, info = env.step(action)

    #     episode_over = terminated or truncated

    # env.close()