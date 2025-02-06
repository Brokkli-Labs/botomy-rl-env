from collections import defaultdict
import gymnasium as gym
import numpy as np
import pickle
import os
from datetime import datetime


class BotomyAgent:
    def __init__(
        self,
        env: gym.Env,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            env: The training environment
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs: tuple[int, int, bool]) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        obs_tuple = tuple(obs)  # Convert observation to a hashable type
        # with probability epsilon return a random action to explore the environment
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
            # return np.random.randint(0, 4)
        # with probability (1 - epsilon) act greedily (exploit)
        else:
            return int(np.argmax(self.q_values[obs_tuple]))

    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        obs_tuple = tuple(obs)  # Convert observation to a hashable type
        next_obs_tuple = tuple(next_obs)  # Convert next observation to a hashable type
        future_q_value = (not terminated) * np.max(self.q_values[next_obs_tuple])
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[obs_tuple][action]
        )

        self.q_values[obs_tuple][action] = (
            self.q_values[obs_tuple][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)

    def save(self, filepath: str = None) -> str:
        if filepath is None:
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f'models/agent_{timestamp}.pkl'
            
        # Save agent state
        state = {
            'q_values': self.q_values,
            'epsilon': self.epsilon,
            'lr': self.lr,
            'discount_factor': self.discount_factor,
            'epsilon_decay': self.epsilon_decay,
            'final_epsilon': self.final_epsilon,
            'training_error': self.training_error
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
            
        return filepath
    
    @classmethod
    def load(cls, filepath: str) -> 'BotomyAgent':
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
            
        agent = cls(
            learning_rate=state['lr'],
            epsilon_decay=state['epsilon_decay'],
            final_epsilon=state['final_epsilon']
        )
        
        agent.q_values = state['q_values']
        agent.epsilon = state['epsilon']
        agent.discount_factor = state['discount_factor']
        agent.training_error = state['training_error']
        
        return agent