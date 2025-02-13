# Botomy RL Environment

This project is a reinforcement learning environment using FastAPI.

## Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/botomy-rl-env.git
   cd botomy-rl-env
   ```

2. Create and activate a virtual environment:

   ```sh
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the env which starts a fastapi server on port 3000

   ```sh
   python main.py --train=true
   
   # set other params..
   python main.py --n_steps 1000 --n_epochs 2 --total_timesteps 100000 --checkpoint_freq 1000 --max_episode_steps 1000 --train True --log_path "./logs"  --checkpoint_path "./checkpoints"  --model_path "model.zip"
   
   # inference
   python main.py --n_steps 1000 --n_epochs 2 --total_timesteps 100000 --checkpoint_freq 1000 --max_episode_steps 1000 --train False --model_path "checkpoints/ppo-mlp-20250213-0819_100000_steps.zip"
   
   # help
   python main.py --help
   ```

2. Start the game in rl training mode

on Mac:

```
open /Applications/Botomy.app/ --args -- --rl_training_mode=true
```

Windows:

```
Botomy.exe -- --rl_training_mode=true
```

You can go headless too
e.g.

```
open /Applications/Botomy.app/ --args --headless -- --rl_training_mode=true
```

3. Tensorboard

https://stable-baselines3.readthedocs.io/en/master/guide/tensorboard.html

```shell
tensorboard --logdir ./logs/
```

http://localhost:6006/


## API Endpoints

- `POST /`: Accepts level data and returns an empty list.
- `GET /reset`: Resets the environment and returns `True`.

## License

This project is licensed under the MIT License.
