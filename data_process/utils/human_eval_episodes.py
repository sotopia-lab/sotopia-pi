# code to prepare and select conversation for human eval 
import sys
import os
os.environ[
    "REDIS_OM_URL"
] = "redis://:PASSWORD@tiger.lti.cs.cmu.edu:6388"
import json
from tqdm.notebook import tqdm
from sotopia.database.persistent_profile import AgentProfile, EnvironmentProfile, RelationshipProfile
from sotopia.database.logs import EpisodeLog
from sotopia.database.env_agent_combo_storage import EnvAgentComboStorage
from redis_om import Migrator
import random
import numpy as np
import pandas as pd
from redis_filtering import get_clean_episodes, align_episode_by_env, goal_filter_all_env_agent
from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import EnvironmentProfile
from prompt_reverse_engineering import concat_episode_msg

SELECTED_TAG = ['sft-round-2_checkpoint_improve-0_epoch-20_gpt-3.5-turbo_test'] 
#["gpt-4_gpt-3.5-turbo_v0.0.1_clean"]
#["sft_round_1_gpt-4_gpt-4_clean"] 
#["ft-mistral-7b-old-filtererd-data_gpt-3.5_clean_ruiyi_1116"] 

# difficulty could vary by agent - same scenario might be hard for one and normal for the other
# for our purpose, it is fair to use dialogue, regardless of agents, in hard testing set 
HARD_SCENARIO = set(['01H7VFHNV13MHN97GAH73E3KM8', '01H7VFHN5WVC5HKKVBHZBA553R', '01H7VFHNN7XTR99319DS8KZCQM', 
                 '01H7VFHN9W0WAFZCBT09PKJJNK', '01H7VFHPDZVVCDZR3AARA547CY', '01H7VFHPQQQY6H4DNC6NBQ8XTG', 
                 '01H7VFHPQQQY6H4DNC6NBQ8XTG', '01H7VFHN7WJK7VWVRZZTQ6DX9T', '01H7VFHN7A1ZX5KSMT2YN9RXC4', 
                 '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHNN7XTR99319DS8KZCQM', 
                 '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHPSWGDGEYRP63H2DJKV0', 
                 '01H7VFHPSWGDGEYRP63H2DJKV0', '01H7VFHNF4G18PC9JHGRC8A1R6', '01H7VFHNNYH3W0VRWVY178K2TK', 
                 '01H7VFHP8AN5643B0NR0NP00VE', '01H7VFHN7A1ZX5KSMT2YN9RXC4'])

CHECK_STR = "Prompt after formatting:\nHere is the context of this interaction"


def random_select_epsiode(tag, selected_scenarios, item_num):
    episode_by_tag = get_clean_episodes(tag)
    concat_epilist = sum(episode_by_tag.values(), [])
    dic_epi_env = align_episode_by_env(concat_epilist)
    select_list = []
    for env, epilist in dic_epi_env.items():
        if env in selected_scenarios:
            rand_epis = random.sample(epilist, item_num)
            select_list.append(rand_epis)

    return sum(select_list, [])

def check_match_reward_prompts(episode):
    """
    Function to check if the episode log has the correct reward prompts corresponding to messages
    """
    party1 = episode.messages[0][0][1]
    party2 = episode.messages[0][1][1]
    if party1 not in episode.rewards_prompt or party2 not in episode.rewards_prompt or CHECK_STR not in episode.rewards_prompt:
        return False
    return True
    

def filter_correct_reward_prompt_epsiode(dic_epi_env, scenarios):
    dialog_sample = [] 
    for env in scenarios: 
        all_episodes = dic_epi_env[env]
        for episode in all_episodes:
            if check_match_reward_prompts(episode):
                 dialog_sample.append(episode)
    # dialog_sample = sum(dialog_sample, [])
    return dialog_sample


def check_correct_num(dialog_samples):
    count_dict = {}
    for episode in dialog_samples:
        if episode.environment not in count_dict:
            count_dict[episode.environment] = []
        count_dict[episode.environment].append(episode)

    counts = 0
    for k, v in count_dict.items():
        print(k, len(v))
        counts+=len(v)
    print(len(count_dict))
    print(counts)


def episode_to_json(filename, selected_episodes):
    dir = os.getcwd()+"/"+filename
    if not os.path.exists(dir):
            os.makedirs(dir)

    for episode_pk in selected_episodes:#dialog_sample:
        episode = EpisodeLog.get(pk=episode_pk)
        json_dict = {}
        json_dict['pk'] = episode.pk
        json_dict['environment'] = episode.environment
        json_dict['tag'] = episode.tag
        json_dict['models'] = episode.models
        context1 = episode.messages[0][0][2].split("Conversation Starts:")[0]
        context2 = episode.messages[0][1][2].split("Conversation Starts:")[0]
        messages = concat_episode_msg(episode)
        messages = messages.split("Conversation Starts:")[1]
        reward_prompt = episode.rewards_prompt
        reward_prompt = reward_prompt.split("\nBased on previous interactions")[0]
        require_manual = False
        if check_match_reward_prompts(episode):
            json_dict['rewards_prompt'] = reward_prompt
        else:
            # if not correct, we need to fix the prompt using messages
            json_dict['context2'] = context2
            json_dict['rewards_prompt'] = "Prompt after formatting:"+context1+messages 
            require_manual = True 

        jsondump = json.dumps(json_dict, indent=4)
        jsonname = "/MANUAL-{}.json".format(episode.pk) if require_manual else "/{}.json".format(episode.pk)
        with open(dir+jsonname, "w") as f:
            f.write(jsondump)
            count+=1
    print(count)