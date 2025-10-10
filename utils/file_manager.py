import os
import json
import pickle
from datetime import datetime

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
        model_files = [f for f in files if f.endswith('.pkl')]
        result = []
        for filename in model_files:
            metadata = self._load_metadata(filename)
            result.append((filename, metadata))
        return result

    #saves a model
    def save_model(self, agent, model_name=None, metadata=None):
        self.ensure_directory_exists()
        filename = self.generate_model_name(model_name)
        if not filename.endswith('.pkl'):
            filename += '.pkl'
        filepath = os.path.join(self.models_dir, filename)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(agent, f)
            if metadata:
                self._save_metadata(filename, metadata)
            return filepath
        except Exception as e:
            print(f"Error saving model: {e}")
            return None

    # loads the model
    def load_model(self, model_name):
        if not model_name.endswith('.pkl'):
            model_name += '.pkl'
        filepath = os.path.join(self.models_dir, model_name)
        try:
            with open(filepath, 'rb') as f:
                agent = pickle.load(f)
            return agent
        except FileNotFoundError:
            print(f"Model {model_name} not found")
            return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

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
        return self._load_metadata(model_name + '.pkl')

    # saves the data about the model
    def _save_metadata(self, model_name, metadata):
        metadata_filename = model_name.replace('.pkl', '.json')
        metadata_path = os.path.join(self.models_dir, metadata_filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)  # indent=2 makes it readable

    # loads the models data
    def _load_metadata(self, model_name):
        metadata_filename = model_name.replace('.pkl', '.json')
        metadata_path = os.path.join(self.models_dir, metadata_filename)
        # Try to load the JSON file
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # No metadata found, return empty dict