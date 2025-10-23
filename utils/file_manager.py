import os
import json
from collections import deque
from datetime import datetime

import keras

"""
Model Manager class
manages the different saved models
contains functions that help load, save, and use models
"""
class ModelManager:
    #initialize the model
    def __init__(self, models_dir="models/saved_models"):
        self.models_dir = models_dir
        self.ensure_directory_exists()

    #make sure that the pathway exists
    def ensure_directory_exists(self):
        os.makedirs(self.models_dir, exist_ok=True)

    #checks if the user has chosen a name, otherwise creates one with datetime format
    def generate_model_name(self, custom_name=None):
        if custom_name is not None:
            return custom_name
        else:
            return f"connect4_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    # gives the user a list of presaved models to choose from when loading models
    def list_saved_models(self):
        if not os.path.exists(self.models_dir):
            return []
        files = os.listdir(self.models_dir)
        model_files = [f for f in files if f.endswith('.keras')]
        result = []
        for filename in model_files:
            metadata = self.load_metadata(filename)
            result.append((filename, metadata))
        return result

    #saves a model
    def save_model(self, agent, model_name=None, metadata=None):
        self.ensure_directory_exists()
        if model_name.endswith(".pkl"):
            model_name = model_name[:-4]
        filepath = os.path.join(self.models_dir, model_name)
        # Save model weights
        agent.save_model(filepath + '.keras')
        # Save additional training metadata
        if metadata is None:
            metadata = {}
            # Convert non-serializable objects
        serializable_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, deque):
                # Convert deque to list
                serializable_metadata[key] = list(value)
            elif hasattr(value, 'tolist'):
                # Handle numpy arrays
                serializable_metadata[key] = value.tolist()
            else:
                serializable_metadata[key] = value

        # Save metadata
        try:
            with open(filepath + '_metadata.json', 'w') as f:
                json.dump(serializable_metadata, f)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    # loads the model
    def load_model(self, model_name):
        if model_name.endswith(".pkl"):
            model_name = model_name[:-4]
        if not model_name.endswith(".keras"):
            model_name = model_name + ".keras"
        filepath = os.path.join(self.models_dir, model_name)
        # Load model weights
        model = keras.models.load_model(filepath)
        # Load metadata
        try:
            with open(filepath + '_metadata.json', 'r') as f:
                metadata = json.load(f)
            # Restore training state
            self.total_episodes = metadata.get('episodes', 0)
            self.epsilon = metadata.get('epsilon', 1.0)

            # Restore memory if applicable
            if 'memory' in metadata:
                self.memory = deque(metadata['memory'], maxlen=2000)
        except FileNotFoundError:
            print("No metadata found, starting from scratch")
        except Exception as e:
            print(f"Error loading metadata: {e}")
        return model

    #deletes unwanted models
    def delete_model(self, model_name):
        try:
            os.remove(os.path.join(self.models_dir, model_name + '.pkl'))
            os.remove(os.path.join(self.models_dir, model_name + '.json'))
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error deleting model: {e}")
            return False

    #gets the information from the model to be used
    def get_model_info(self, model_name):
        return self.load_metadata(model_name + '.keras')

    # saves the data about the model
    def save_metadata(self, model_name, metadata):
        metadata_filename = model_name.replace('.keras', '_metadata.json')
        metadata_path = os.path.join(self.models_dir, metadata_filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)  # indent=2 makes it readable

    # loads the models data
    def load_metadata(self, model_name):
        metadata_filename = model_name.replace('.keras', '_metadata.json')
        metadata_path = os.path.join(self.models_dir, metadata_filename)
        # Try to load the JSON file
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # No metadata found, return empty dict
