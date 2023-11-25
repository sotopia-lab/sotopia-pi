# conda env config vars set REDIS_OM_URL="redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"
import os
import sys
import yaml
import json
from sotopia.database.logs import EpisodeLog
from data_process.redis_data_filtering.prompt_reverse_engineering import parse_prompt_to_json
from data_process.llama_factory_data_preprocess import join_json_files

sys.path.append('../')

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    
os.environ["REDIS_OM_URL"] = config.redis_om_url

def preprocess_episodes(episodes):
    for episode in episodes:
        parse_prompt_to_json(episode, dir="./raw_json/", init_speak=True, include_format=False)
        parse_prompt_to_json(episode, dir="./raw_json/", init_speak=False, include_format=False)
    data = join_json_files("./raw_json/")
    
    with open("../llm_rl/data/sotopia_custom_training_sft.json", 'w') as f:
        json.dump(data, f, indent=4)

def preprocess_episodes_with_tag(tag):
    episodes = list(EpisodeLog.find(EpisodeLog.tag==tag).all())
    preprocess_episodes(episodes)