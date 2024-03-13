import os
import sys

os.environ["REDIS_OM_URL"] = "redis://:password@server_name:port_num"
import argparse
import json

import yaml
from redis_filtering import (
    filter_pks_to_prompts,
    get_env_mean_var,
    get_episode_by_env,
    get_threshold_by_keep_rate,
    goal_reward_by_env_agent,
)
from redis_om import Migrator
from tqdm.notebook import tqdm


def read_item_list(filepath):
    with open(filepath, "r") as file:
        item_list = file.read().split("\n")
    return item_list


def main():
    with open(
        os.getcwd() + "/data_process/redis_data_filtering/filter_args.yml", "r"
    ) as file:
        args = yaml.safe_load(file)
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--tag_list",
    #     type=str,
    #     default="",
    #     # required=True,
    #     help="a list of tag for apply filter on",
    # )

    # parser.add_argument(
    #     "--sotopia",
    #     type=str,
    #     default="false",
    #     help="to use all sotopia scenarios",
    # )
    # parser.add_argument(
    #     "--generated",
    #     type=str,
    #     default="true",
    #     help="to use all generated scenarios",
    # )
    # parser.add_argument(
    #     "--scenario_list",
    #     type=str,
    #     default="",
    #     help="bespoke list of scenario pks",
    # )
    # parser.add_argument(
    #     "--output_dir",
    #     type=str,
    #     default=os.getcwd(),
    #     help="directory to save the generated completion propmts",
    # )
    # parser.add_argument(
    #     "--reward", type=str, default="goal", help="type of reward score used for filtering"
    # )
    # parser.add_argument(
    #     "--reward_cutoff", type=float, default=7, help="threshold for filtering by the reward type"
    # )
    # parser.add_argument(
    #     "--balance", type=str, default='true', help="whether we want to balance #agent1 and #agent2"
    # )
    # parser.add_argument(
    #     "--includeformat", type=str, default='false', help="whether we want to include format in prompt reverse"
    # )

    # args = parser.parse_args()
    tags, selected_envs = [], []
    if args["tag_list"] != "":
        tags = read_item_list(args["tag_list"])
    if args["scenario_list"] != "":
        selected_envs = read_item_list(args["scenario_list"])

    use_only_sotopia = args["sotopia"]
    use_only_gen = args["generated"]
    filter_score = args["reward"]
    filter_cutoff = args["reward_cutoff"]
    if_balance = args["balance"]
    include_format = args["includeformat"]

    env_episodes = get_episode_by_env(
        tags, use_only_sotopia, use_only_gen, selected_envs
    )
    # env_rewards, env_pks = goal_reward_by_env_agent(env_episodes, filter_score)
    # env_mean_var = get_env_mean_var(env_rewards)
    filter_env_rewards, filter_env_pks = goal_reward_by_env_agent(
        env_episodes, filter_score, filter_cutoff, balance=if_balance
    )
    # filter_env_mean_var = get_env_mean_var(filter_env_rewards)
    filter_pks_to_prompts(filter_env_pks, args["output_dir"], include_format)
    print(
        "Finishing generating prompts for {} env agent pairs".format(
            len(filter_env_pks)
        )
    )


if __name__ == "__main__":
    main()
