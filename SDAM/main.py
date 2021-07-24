
import os
import sys
print(os.path.abspath(__file__))


import yaml


if __name__ == "__main__":
    
    print("aaaaaaaaaaaaaaaa")
    with open('./config.yaml') as f:
        config = yaml.safe_load(f)

    print(config)
    print("Aa")