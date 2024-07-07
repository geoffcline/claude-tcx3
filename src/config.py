import yaml

config = None

def load_config(config_path):
    global config
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

def get_config():
    if config is None:
        raise ValueError("Configuration not loaded. Call load_config() first.")
    return config