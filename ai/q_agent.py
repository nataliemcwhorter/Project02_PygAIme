import numpy as np
import random
import os
import tensorflow as tf
from tensorflow import keras
from collections import deque


class QAgent:
    def __init__(self, state_size=42, action_size=7, learning_rate=0.001):
        self.state_size = state_size  # 6x7 board flattened
        self.action_size = action_size  # 7 possible columns
        self.learning_rate = learning_rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.memory = deque(maxlen=2000)
        self.q_network = self._build_model()
        self.target_network = self._build_model()
        self.total_episodes = 0
        self.models_dir = "models/saved_models"

    def _build_model(self):
        model = keras.Sequential()
        model.add(keras.layers.Dense(128, input_shape=(self.state_size,), activation='relu'))
        model.add(keras.layers.Dense(128, activation='relu'))
        model.add(keras.layers.Dense(self.action_size))
        model.compile(optimizer='adam', loss='mse')
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, valid_moves):
        if random.random() <= self.epsilon:
            return random.choice(valid_moves)
        else:
            q_values = self.q_network.predict(state.reshape(1, -1))[0]
            for move in valid_moves:
                valid_q_values = [(move, q_values[move])]
            return max(valid_q_values, key=lambda x: x[1])[0]

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        states = []
        targets = []
        for state, action, reward, next_state, done in batch:
            state = state.reshape(1, -1)
            next_state = next_state.reshape(1, -1)
            target = self.q_network.predict(state)[0]
            if done:
                target[action] = reward
            else:
                next_q_values = self.target_network.predict(next_state)[0]
                target[action] = reward + 0.95 * np.max(next_q_values)
            states.append(state[0])
            targets.append(target)
        self.q_network.fit(np.array(states), np.array(targets), epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target_network(self):
        self.target_network.set_weights(self.q_network.get_weights())

    def save_model(self, filepath):
        if not filepath.endswith('.keras'):
            filepath += '.keras'
        self.q_network.save(filepath, save_format='keras')
        metadata = {
            'episodes': getattr(self, 'total_episodes', 0),
            'epsilon': getattr(self, 'epsilon', 1.0),
            'memory': list(self.memory) if hasattr(self, 'memory') else [],
            # Add other relevant training state information
        }
        return metadata

    def load_model(self, filepath):
        if filepath.endswith('.pkl'):
            filepath = filepath[:-4]
        if not filepath.endswith('.keras'):
            filepath = filepath + '.keras'
        filep = os.path.join(self.models_dir, filepath)
        self.q_network = keras.models.load_model(filep)
        self.target_network.set_weights(self.q_network.get_weights())

    def get_training_stats(self):
        return {
            'epsilon': self.epsilon,
            'memory_size': len(self.memory),
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay
        }