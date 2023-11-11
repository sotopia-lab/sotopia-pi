import argparse
import os
from collections import defaultdict
from typing import Any, Dict, List, Tuple, Union, cast

import pandas as pd
import rich
from rich.console import Console
from rich.terminal_theme import MONOKAI

from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import EnvironmentProfile
from prompt_reverse_engineering import parse_prompt_to_json
import numpy as np
import json


TRAIN_LOGS = r'train_logs' 
TEST_LOGS = r'test_logs' 

OVERALL_REWARD_FILTER = 3.2   
GOAL_AVG_THRESHOLD = 7
GOAL_KEEP_THRESHOD = 7

SELECTED_TAG = [#"gpt-3.5-turbo_gpt-3.5-turbo_v0.0.1_clean", 
                #"gpt-4_gpt-3.5-turbo_v0.0.1_clean", 
                "gpt-4_gpt-4_v0.0.1_clean",
                # "gpt-4_togethercomputer/mpt-30b-chat_v0.0.1_clean"
                ]

HARD_SCENARIO = set(['01H7VFHNV13MHN97GAH73E3KM8', '01H7VFHN5WVC5HKKVBHZBA553R', '01H7VFHNN7XTR99319DS8KZCQM', 
                 '01H7VFHN9W0WAFZCBT09PKJJNK', '01H7VFHPDZVVCDZR3AARA547CY', '01H7VFHPQQQY6H4DNC6NBQ8XTG', 
                 '01H7VFHPQQQY6H4DNC6NBQ8XTG', '01H7VFHN7WJK7VWVRZZTQ6DX9T', '01H7VFHN7A1ZX5KSMT2YN9RXC4', 
                 '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHNN7XTR99319DS8KZCQM', 
                 '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHPSWGDGEYRP63H2DJKV0', 
                 '01H7VFHPSWGDGEYRP63H2DJKV0', '01H7VFHNF4G18PC9JHGRC8A1R6', '01H7VFHNNYH3W0VRWVY178K2TK', 
                 '01H7VFHP8AN5643B0NR0NP00VE', '01H7VFHN7A1ZX5KSMT2YN9RXC4'])
 # use new branch redis_agent to extra 

def get_clean_episodes(selected_tags=SELECTED_TAG):
    selected_episodes = {}
    for tag in selected_tags:
        tag_epis = EpisodeLog.find(EpisodeLog.tag == tag).all()
        if len(tag_epis) > 0:
            selected_episodes[tag]=tag_epis
    
    return selected_episodes

def episode_by_env(episode_list):
    # align episodes with its scenarios
    env_set = set()
    episode_env_dict: dict[str, list[EpisodeLog]] = {}
    for episode in episode_list:
        env = episode.environment
        if env not in env_set:
            env_set.add(env)
            episode_env_dict[env] = []
        episode_env_dict[env].append(episode)

    return episode_env_dict


def goal_reward_by_env_agent(env_epi_dic):
    reward_dic = {}
    for env, episodes in env_epi_dic.items():
        goal_score = {'agent1':[], 'agent2':[]}
        for episode in episodes:
            rewards = episode.rewards
            goal_score['agent1'].append(rewards[0][1]['goal'])
            goal_score['agent2'].append(rewards[1][1]['goal'])
        reward_dic[env] = goal_score

    return reward_dic

def goal_filter_per_env_agent(episodes):
    # filter using goal reward scores for each agent position given scenario
    goal_score = {'agent1':[], 'agent2':[]}
    env_tpls = []
    # at least need to have half of the total len of the dialogue amount per scenario
    # then add the filtering by score
    min_threshold_amt = len(episodes) // 2
    for episode in episodes:
        rewards = episode.rewards
        goal_score['agent1'].append(rewards[0][1]['goal'])
        goal_score['agent2'].append(rewards[1][1]['goal'])

    agent1_avg = np.mean(goal_score['agent1'])
    agent2_avg = np.mean(goal_score['agent2'])
    agent1_rank = np.argsort(goal_score['agent1'])
    agent2_rank = np.argsort(goal_score['agent2'])

    for i in range(len(episodes)):
        # maintain min required # of dialogue for each agent in each scenario
        if i > (min_threshold_amt):
            env_tpls.append((episodes[agent1_rank[i]], 0))
            env_tpls.append((episodes[agent2_rank[i]], 1))
        else:
            if goal_score['agent1'][agent1_rank[i]] >= min(GOAL_KEEP_THRESHOD, agent1_avg) and (goal_score['agent2'][agent2_rank[i]] >= min(GOAL_KEEP_THRESHOD, agent2_avg)):
                env_tpls.append((episodes[agent1_rank[i]], 0))
                env_tpls.append((episodes[agent1_rank[i]], 1))
                
    return env_tpls


def goal_filter_all_env_agent(env_episode_dic):
    filter_env_dic = {}
    for env, episodes in env_episode_dic.items():
        env_agent_episode = goal_filter_per_env_agent(episodes)
        filter_env_dic[env] = env_agent_episode
        
    return filter_env_dic


def run_filtered_episodes_to_prompt(filter_env_agent_episodes, json_dir, level="Easy"):
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    parse_count = 0
    for env, tpls in filter_env_agent_episodes.items():
        if (level == 'Easy' and env in HARD_SCENARIO) or (level == 'Hard' and env not in HARD_SCENARIO):
            continue
        for tpl in tpls:
            parse_prompt_to_json(tpl[0], json_dir, tpl[1])
            parse_count+=1

    print(parse_count)


"""----------->Functions that were used for different approaches of DP, mostly depreciated<------------ """

def overall_reward_by_env(episode_env_dict):
    # for each scenario, append all episode's overall score
    env_score_dic = {}
    for env, epilist in episode_env_dict.items():
        env_score_dic[env] = []
        for epi in epilist:
        #max_reward = max(max_reward, epi.rewards[0][0])
            env_score_dic[env].append(epi.rewards[0][0])

    return env_score_dic

def filter_episode_by_overall(env_list, env_episode_dic, THRES=OVERALL_REWARD_FILTER):
    """
    Return list of Episode
    """
    result_episodes = []
    for env in env_list:
        epilist = env_episode_dic[env]
        for epi in epilist:
            if epi.rewards[0][0] >= THRES:
                result_episodes.append(epi)     

    return result_episodes

def filter_goal_reward_by_env(episode_env_dict):
    # deprecate function 
    env_scores, filter_dic = {}, {}
    for env, episodes in episode_env_dict.items():
        goal_score = []
        for episode in episodes:
            rewards = episode.rewards
            for r in rewards:
                goal_score.append(r[1]['goal']) # r is a tuple, the 2nd element is a dict of scores
        
        env_scores[env] = goal_score
        env_avg = np.mean(goal_score)

        filter_epis = []
        for episode in episodes:
            rewards = episode.rewards
            avg_reward = 0.5*(rewards[0][1]['goal']+rewards[1][1]['goal'])
            if avg_reward > min(env_avg, GOAL_AVG_THRESHOLD): # using 6.5 only reduce to 416 from 450, use 7 reduce to 388
                filter_epis.append(episode)
        filter_dic[env] = filter_epis   
        
    #print(len(sum(filter_dic.values(), [])), len(sum(dic_epi_env.values(), [])))
    return env_scores, filter_dic

def split_env_by_variance(env_score_dic, split_ratio=0.7):
    # calculate variance of each scenario
    env_var_dic = {}
    for env, scores in env_score_dic.items():
        env_var = np.var(scores)
        env_var_dic[env] = env_var
    sorted_env = sorted(env_var_dic)
    # split into normal vs hard by variance
    split_env_dic = {}
    split_env_dic['normal'] = sorted_env[:int(len(sorted_env)*split_ratio)]
    split_env_dic['hard'] = sorted_env[int(len(sorted_env)*split_ratio):]

    return split_env_dic


def pull_dialogue_by_select(select_episodes, to_json=False, json_dir=""):
    # this convert episodelog into chat format, not completion format
    all_msg = []
    for epi in select_episodes:
        #epi = EpisodeLog.get(epi_id)
        all_msg.append(epi) #
    
    if to_json:
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        for epi in all_msg:
            epi_json=json.dumps(dict(epi), indent=4)
            with open(json_dir+"/{}.json".format(epi.pk), "w") as f:
                f.write(epi_json)
    return all_msg

