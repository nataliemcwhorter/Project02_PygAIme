import random
import numpy as np
from game.board import Connect4Board
from utils.file_manager import ModelManager


class TrainingManager:
    def __init__(self, agent, board):
        self.model_name = None
        self.training_stats = {
            'episodes': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0.0,
            'total_episodes': 0
        }
        self.agent = agent
        self.model_manager = ModelManager()
        self.board = board

    def initialize(self, model_name):
        self.model_name = model_name
        self.training_stats['total_episodes'] = self.model_manager.load_metadata(self.model_name)

    def train(self, mode='self_play', **kwargs):
        valid_modes = ['self_play', 'vs_random', 'vs_human']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode. Choose from {valid_modes}")
        try:
            if mode == 'self_play':
                episodes = kwargs.get('episodes')
                return self._train_self_play(episodes)
            elif mode == 'vs_random':
                episodes = kwargs.get('episodes')
                return self._train_against_random(episodes)
            elif mode == 'vs_human':
                human_move_callback = kwargs.get('human_move_callback')
                if not human_move_callback:
                    raise ValueError("Human move callback required for human training mode")
                return self._train_against_human(human_move_callback)
        except Exception as e:
            print(f"Training Error: {e}")
            raise

    def _self_play_episode(self):
        self.board.reset()
        current_player = random.randint(1, 2)
        while True:
            state = self.board.get_board_state()
            valid_moves = self.board.get_valid_moves()
            if not valid_moves:
                return 0
            action = self.agent.act(state, valid_moves)
            prev_state = state
            row = self.board.make_move(action, current_player)
            new_state = self.board.get_board_state()
            if self.board.check_winner(current_player, row, action):
                if current_player == 1:
                    reward = 100
                else:
                    reward = -100
                self.agent.remember(prev_state, action, reward, new_state, True)
                return current_player
            self.agent.remember(prev_state, action, -1, new_state, False)
            current_player = 3-current_player

    def _train_self_play(self, episodes):
        self.reset_stats()
        for episode in range(episodes):
            result = self._self_play_episode()
            if result == 1:
                self.training_stats['wins'] += 1
            elif result == 2:
                self.training_stats['losses'] += 1
            elif result == 0:
                self.training_stats['draws'] += 1
            self.training_stats['episodes'] += 1
            self.training_stats['total_episodes'] += 1
            self.training_stats['win_rate'] = self.training_stats['wins'] / self.training_stats['episodes']
            self.agent.replay()
            if episode % 10 == 0:
                self.agent.update_target_network()
            if episode % 100 == 0 or episode % 100 == 1:
                self.get_training_progress()
        print(f"Final Epsilon: {self.agent.epsilon}")
        self.training_stats['final_epsilon'] = self.agent.epsilon
        return self.training_stats

    def _train_against_random(self, episodes):
        self.reset_stats()
        for episode in range(episodes):
            self.board.reset()
            current_player = 1
            while True:
                state = self.board.get_board_state()
                valid_moves = self.board.get_valid_moves()
                if not valid_moves:
                    self.training_stats['draws'] += 1
                    break
                if current_player == 1:
                    action = self.agent.act(state, valid_moves)
                    prev_state = state
                else:
                    action = random.choice(valid_moves)
                    prev_state = state
                row = self.board.make_move(action, current_player)
                new_state = self.board.get_board_state()
                if self.board.check_winner(current_player, row, action):
                    if current_player == 1:
                        self.training_stats['wins'] += 1
                        reward = 100
                    else:
                        self.training_stats['losses'] += 1
                        reward = -100
                    self.agent.remember(prev_state, action, reward, new_state, True)
                    break
                if current_player == 1:
                    self.agent.remember(prev_state, action, -1, new_state, False)
                current_player = 3-current_player
            self.training_stats['episodes'] += 1
            self.training_stats['total_episodes'] += 1
            self.training_stats['win_rate'] = self.training_stats['wins'] / self.training_stats['episodes']
            self.agent.replay()
            if episode % 10 == 0:
                self.agent.update_target_network()
            if episode % 100 == 0 or episode % 100 == 1:
                self.get_training_progress()
        print(f"Final Epsilon: {self.agent.epsilon}")
        self.training_stats['final_epsilon'] = self.agent.epsilon
        return self.training_stats

    def _train_against_human(self, human_move_callback):
        self.reset_stats()
        current_player = random.randint(1, 2)
        self.board.reset()
        while True:
            state = self.board.get_board_state()
            valid_moves = self.board.get_valid_moves()
            if not valid_moves:
                self.training_stats['draws'] += 1
                break
            if current_player == 1:
                action = self.agent.act(state, valid_moves)
                prev_state = state
            else:
                action = human_move_callback(valid_moves)
                prev_state = state
            row = self.board.make_move(action, current_player)
            new_state = self.board.get_board_state()
            if self.board.check_winner(current_player, row, action):
                if current_player == 1:
                    self.training_stats['wins'] += 1
                    reward = 100
                else:
                    self.training_stats['losses'] += 1
                    reward = -100
                self.agent.remember(prev_state, action, reward, new_state, True)
                break
            if current_player == 1:
                self.agent.remember(prev_state, action, -1, new_state, False)
            current_player = 3-current_player
        self.training_stats['episodes'] += 1
        self.training_stats['total_episodes'] += 1
        self.training_stats['win_rate'] = self.training_stats['wins'] / self.training_stats['episodes']
        self.agent.replay()
        self.training_stats['final_epsilon'] = self.agent.epsilon
        self.get_training_progress()
        return self.training_stats

    def evaluate_agent(self, num_games=100):
        self.reset_stats()
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0
        for episode in range(num_games):
            self.board.reset()
            current_player = 1
            while True:
                state = self.board.get_board_state()
                valid_moves = self.board.get_valid_moves()
                if not valid_moves:
                    self.training_stats['draws'] += 1
                    break
                if current_player == 1:
                    action = self.agent.act(state, valid_moves)
                    prev_state = state
                else:
                    action = random.choice(valid_moves)
                    prev_state = state
                row = self.board.make_move(action, current_player)
                new_state = self.board.get_board_state()
                if self.board.check_winner(current_player, row, action):
                    if current_player == 1:
                        self.training_stats['wins'] += 1
                        reward = 100
                    else:
                        self.training_stats['losses'] += 1
                        reward = -100
                    self.agent.remember(prev_state, action, reward, new_state, True)
                    break
                if current_player == 1:
                    self.agent.remember(prev_state, action, -1, new_state, False)
                current_player = 3 - current_player
            self.training_stats['episodes'] += 1
            self.training_stats['total_episodes'] += 1
            self.training_stats['win_rate'] = self.training_stats['wins'] / self.training_stats['episodes']
            if episode % 100 == 0 or episode % 100 == 1:
                self.get_training_progress()
        self.agent.epsilon = original_epsilon
        print(f"Final Epsilon: {self.agent.epsilon}")
        self.training_stats['final_epsilon'] = self.agent.epsilon
        return self.training_stats

    def get_training_progress(self):
        print(f"Episode: {self.training_stats['episodes']}")
        print(f"Win Rate: {self.training_stats['win_rate']:.2f}")
        print(f"Total Games Played: {self.training_stats['episodes']}")
        print(f"Wins: {self.training_stats['wins']}")
        print(f"Losses: {self.training_stats['losses']}")
        print(f"Draws: {self.training_stats['draws']}")
        print(f"Current Epsilon: {self.agent.epsilon}")
        print("-------------------------------")

    def reset_stats(self):
        self.training_stats['episodes'] = 0
        self.training_stats['wins'] = 0
        self.training_stats['losses'] = 0
        self.training_stats['draws'] = 0
        self.training_stats['win_rate'] = 0