"""
converted from interactive filtering notebook. 
The code could be run in notebook for visualizing the score distribution

BELOW are instruction in notebook
Please do NOT change anything under <b>Global Fix Variables</b>
<br><br>
Please MAKE changes under <b>Global Flex Variables</b> to fit your need
<br><br>
Once you set everything in <b>Global Flex Variables</b>, click Run All and view the results. 
<br><br><br>
<b>---------------------------------------------------------------------------------</b>
<br>
Range for <b>FILTER_THRESHOLD</b> should be between 0 and 10.
<br><br>
You can enter a list of environment pks under <b>SELECTED_ENV_LIST</b>, so the notebook would only look at conversations under these pks. 
<br><br>
If <b>SELECTED_ENV_LIST</b> is NOT empty, USE_ONLY_GEN and USE_ONLY_SOTOPIA would be ignore.
<br><br>
If <b>SELECTED_ENV_LIST</b> is empty, the environment pks would include either all non-sotopia pks, or all sotopia pks, or both, depending on USE_ONLY_GEN and USE_ONLY_SOTOPIA value.
<br><br>
For IF_BALANCE, this applies to filtering threshold < 10. If set to True, the filtering would automatically balance the number of dialogues for agent 1 and agent 2, and only keep the smaller subset. If set to False, the filtering would keep all dialogues that lead to reward above threshold, so agent 1 and agent 2 could have different total number of filtered dialogues. 
<br><br>
Option for <b>FILTER_SCORE</b> include:
* 'believability'
* 'relationship'
* 'knowledge'
* 'secret'
* 'social_rules'
* 'financial_and_material_benefits'
* 'goal'
* 'overall_score'

"""
import sys
import os
os.environ["REDIS_OM_URL"] = "redis://:password@server_name:port_num"

import json
from tqdm.notebook import tqdm
from sotopia.database.persistent_profile import AgentProfile, EnvironmentProfile, RelationshipProfile
from sotopia.database.logs import EpisodeLog
from sotopia.database.env_agent_combo_storage import EnvAgentComboStorage
from redis_om import Migrator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from redis_filtering import get_sotopia_scenarios, get_generated_scenarios, get_episode_by_env
from redis_filtering import goal_reward_by_env_agent, get_env_mean_var, get_threshold_by_keep_rate, filter_pks_to_prompts
from redis_visualization import plot_agent_reward_distribution, plot_env_reward_distribution, make_pretty

# Global Var
SOTOPIA_HARD_SCENARIO = set(
    ['01H7VFHNV13MHN97GAH73E3KM8', '01H7VFHN5WVC5HKKVBHZBA553R', '01H7VFHNN7XTR99319DS8KZCQM', 
     '01H7VFHN9W0WAFZCBT09PKJJNK', '01H7VFHPDZVVCDZR3AARA547CY', '01H7VFHPQQQY6H4DNC6NBQ8XTG', 
     '01H7VFHPQQQY6H4DNC6NBQ8XTG', '01H7VFHN7WJK7VWVRZZTQ6DX9T', '01H7VFHN7A1ZX5KSMT2YN9RXC4', 
     '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHPS5WJW2694R1MNC8JFY', '01H7VFHNN7XTR99319DS8KZCQM', 
     '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHQ11NAMZS4A2RDGDB01V', '01H7VFHPSWGDGEYRP63H2DJKV0', 
     '01H7VFHPSWGDGEYRP63H2DJKV0', '01H7VFHNF4G18PC9JHGRC8A1R6', '01H7VFHNNYH3W0VRWVY178K2TK', 
     '01H7VFHP8AN5643B0NR0NP00VE', '01H7VFHN7A1ZX5KSMT2YN9RXC4'])
SOTOPIA_SCENARIO_PK = get_sotopia_scenarios()
GEN_SCENARIO_PK = get_generated_scenarios(exclude=SOTOPIA_SCENARIO_PK)
OTHER_SCENARIO_PK = ['01H4EFKY8CXBETGNDNDD08X2MS', '01H4EFKY8H8A4P12S4YYE2DNCC',
                     '01H4EFKY8VCAJJJM8WACW3KYWE', '01H4EFKY91BHEG5GD3VRGGY9YE',
                     '01H6S9W1B2QRVBT0JTZTX8DVEM', '01H6S9W1B9KPXARNHRFTXBAQ6A',
                     '01H6S9W1BFRRT091TCP4E4E66J', '01H6S9W1BMGR7MFRPH0V55J2TD',
                     '01H6S9W1BSQK5WT5Y9RAKSH45J', '01H6S9W1BZVYXYSDG4KR2Z3F4X']

# Global Adjustable Var
TAG_LIST = [] # default to all tags
USE_ONLY_SOTOPIA = False
USE_ONLY_GEN = True
SELECTED_ENV_LIST = OTHER_SCENARIO_PK # [] leave it empty if you want all sotopia, all non-sotopia, or everything
FILTER_SCORE = "goal" 
FILTER_THRESHOLD = 7
KEEP_RATE = 0.75 # this is the amount of data we want to keep, after filtering
IF_BALANCE = True # when filtering, do you want to keep # agent 1 and # agent 2 balance?

# set to False if you want to mix agent1 and agent2 and only see distribution of rewards under an environment
SPLIT_ENV_AGENT_DISPLAY=True 

# ONLY set to true if, after reviewing the filtered result, you want to convert the episodelogs into completion format
TO_PROMPT = False 
# path and folder name to save json of prompts
SAVE_DIR = ""
# most case we ignore formatting, so set to False
INCLUDE_FORMAT = False

# mean, var for full data without filtering
env_episodes = get_episode_by_env(TAG_LIST, USE_ONLY_SOTOPIA, USE_ONLY_GEN, OTHER_SCENARIO_PK)
env_rewards, env_pks = goal_reward_by_env_agent(env_episodes, FILTER_SCORE)
env_mean_var = get_env_mean_var(env_rewards)

"""Threshold Checking"""
approx_threshold = get_threshold_by_keep_rate(env_rewards, KEEP_RATE, IF_BALANCE)
print(approx_threshold)

"""Running Filtering"""
# first select in-range episodes and the scores
filter_env_rewards, filter_env_pks = goal_reward_by_env_agent(
    env_episodes, FILTER_SCORE, FILTER_THRESHOLD, balance=IF_BALANCE)
filter_env_mean_var = get_env_mean_var(filter_env_rewards)

# display strats
filter_stats_df = pd.concat({k: pd.DataFrame(v) for k, v in filter_env_mean_var.items()}).unstack(1)
filter_stats_df.sort_index(inplace=True)
filter_agent1_num =  filter_stats_df['agent1']['count'].sum()
filter_agent2_num =  filter_stats_df['agent2']['count'].sum()
print("Total {} + {} Conversation Across {} Environments.".format(
    filter_agent1_num, filter_agent2_num, len(filter_stats_df), ))
print("Agent 1 reduced by {} ({}% of original). Agent 2 reduced by {} ({}% of original).".format(
    agent1_num - filter_agent1_num, 100*round((filter_agent1_num)/(agent1_num), 2),
    agent2_num - filter_agent2_num, 100*round((filter_agent2_num)/(agent2_num ), 2)))
if filter_agent1_num != filter_agent2_num:
    print("If we want to keep conversations for agent 1 and agent 2 balance, go to the above cell and change BALANCE = True")
    print("Resulting number of conversations would be no more than {} for each agent.".format(min(filter_agent1_num, filter_agent2_num)))
filter_stats_df.style.pipe(make_pretty, max(filter_stats_df['agent1']['var']+filter_stats_df['agent2']['var']))


if TO_PROMPT:
    filter_pks_to_prompts(filter_env_pks, SAVE_DIR, INCLUDE_FORMAT)