import sys
import os
os.environ[
    "REDIS_OM_URL"
] = "redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"
import json
import argparse
from tqdm.notebook import tqdm
from sotopia.database.persistent_profile import AgentProfile, EnvironmentProfile, RelationshipProfile
from sotopia.database.logs import EpisodeLog
from sotopia.database.env_agent_combo_storage import EnvAgentComboStorage
from redis_om import Migrator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from redis_filtering import get_episode_by_env
from redis_filtering import goal_reward_by_env_agent, get_env_mean_var, get_threshold_by_keep_rate, filter_pks_to_prompts


def read_item_list(filepath):
    with open(filepath, "r") as file:
        item_list = file.read().split("\n")
    return item_list

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tag_list",
        type=str,
        default="",
        # required=True,
        help="a list of tag for apply filter on",
    )

    parser.add_argument(
        "--sotopia",
        type=str,
        default="false",
        help="to use all sotopia scenarios",
    )
    parser.add_argument(
        "--generated",
        type=str,
        default="true",
        help="to use all generated scenarios",
    )
    parser.add_argument(
        "--scenario_list",
        type=str,
        default="",
        help="bespoke list of scenario pks",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=os.getcwd(),
        help="directory to save the generated completion propmts",
    )
    parser.add_argument(
        "--reward", type=str, default="goal", help="type of reward score used for filtering"
    )
    parser.add_argument(
        "--reward_cutoff", type=float, default=7, help="threshold for filtering by the reward type"
    )
    parser.add_argument(
        "--balance", type=str, default='true', help="whether we want to balance #agent1 and #agent2"
    )
    parser.add_argument(
        "--includeformat", type=str, default='false', help="whether we want to include format in prompt reverse"
    )

    args = parser.parse_args()
    tags, selected_envs = [], []
    if args.tag_list != "":
        tags = read_item_list(args.tag_list)
    if args.scenario_list != "":
        selected_envs = read_item_list(args.scenario_list)

    use_only_sotopia = args.sotopia == 'true'
    use_only_gen = args.generated == 'true'
    filter_score = args.reward
    filter_cutoff = args.reward_cutoff
    if_balance = args.balance == 'true'
    include_format = args.includeformat == 'true'
    env_episodes = get_episode_by_env(tags, use_only_sotopia, use_only_gen, selected_envs)
    env_rewards, env_pks = goal_reward_by_env_agent(env_episodes, filter_score)
    # env_mean_var = get_env_mean_var(env_rewards)
    filter_env_rewards, filter_env_pks = goal_reward_by_env_agent(
        env_episodes, filter_score, filter_cutoff, balance=if_balance)
    # filter_env_mean_var = get_env_mean_var(filter_env_rewards)
    filter_pks_to_prompts(filter_env_pks, args.output_dir, include_format)
    print("Finishing generating prompts for {} env agent pairs".format(len(filter_env_pks)))



if __name__ == "__main__":
    main()