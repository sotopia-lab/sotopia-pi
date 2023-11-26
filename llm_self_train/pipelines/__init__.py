import yaml
import os

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)
        
os.environ["REDIS_OM_URL"] = config["redis_om_url"]