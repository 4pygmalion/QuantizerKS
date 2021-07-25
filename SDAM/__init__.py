import os
import yaml


def set_key(key):
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config['DART']['KEY'] = key
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

def set_save_dir(dir):
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config['ENV']['SAVE_DIR'] = dir
    with open(config_path, 'w') as f:
        yaml.dump(config, f)  
        print(f"save dir was change with: {dir}")