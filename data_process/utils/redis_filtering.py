import argparse
import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Tuple, Union, cast

import numpy as np
import pandas as pd
import rich
from prompt_reverse_engineering import parse_prompt_to_json
from rich.console import Console
from rich.terminal_theme import MONOKAI
from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import EnvironmentProfile

OVERALL_REWARD_FILTER = 3.2
GOAL_AVG_THRESHOLD = 7
GOAL_KEEP_THRESHOD = 10

SELECTED_TAG = [  # "gpt-3.5-turbo_gpt-3.5-turbo_v0.0.1_clean",
    # "gpt-4_gpt-3.5-turbo_v0.0.1_clean",
    "gpt-4_gpt-4_v0.0.1_clean",
    # "gpt-4_togethercomputer/mpt-30b-chat_v0.0.1_clean"
]

HARD_SCENARIO = set(
    [
        "01H7VFHNV13MHN97GAH73E3KM8",
        "01H7VFHN5WVC5HKKVBHZBA553R",
        "01H7VFHNN7XTR99319DS8KZCQM",
        "01H7VFHN9W0WAFZCBT09PKJJNK",
        "01H7VFHPDZVVCDZR3AARA547CY",
        "01H7VFHPQQQY6H4DNC6NBQ8XTG",
        "01H7VFHPQQQY6H4DNC6NBQ8XTG",
        "01H7VFHN7WJK7VWVRZZTQ6DX9T",
        "01H7VFHN7A1ZX5KSMT2YN9RXC4",
        "01H7VFHPS5WJW2694R1MNC8JFY",
        "01H7VFHPS5WJW2694R1MNC8JFY",
        "01H7VFHNN7XTR99319DS8KZCQM",
        "01H7VFHQ11NAMZS4A2RDGDB01V",
        "01H7VFHQ11NAMZS4A2RDGDB01V",
        "01H7VFHPSWGDGEYRP63H2DJKV0",
        "01H7VFHPSWGDGEYRP63H2DJKV0",
        "01H7VFHNF4G18PC9JHGRC8A1R6",
        "01H7VFHNNYH3W0VRWVY178K2TK",
        "01H7VFHP8AN5643B0NR0NP00VE",
        "01H7VFHN7A1ZX5KSMT2YN9RXC4",
    ]
)
# use new branch redis_agent to extra


def get_clean_episodes(selected_tags=SELECTED_TAG):
    # function to get episode by tag
    selected_episodes = {}
    for tag in selected_tags:
        tag_epis = EpisodeLog.find(EpisodeLog.tag == tag).all()
        if len(tag_epis) > 0:
            selected_episodes[tag] = tag_epis

    return selected_episodes


def get_sotopia_scenarios():
    # function to get all sotopia scenario pk
    # we use gpt4-gpt4 tag to collect all sotopia scenario, other clean tags should do the same thing
    tag = "gpt-4_gpt-4_v0.0.1_clean"
    tag_epis = EpisodeLog.find(EpisodeLog.tag == tag).all()
    sotopia_env_pk = set([episode.environment for episode in tag_epis])
    return list(sotopia_env_pk)


def get_generated_scenarios(exclude):
    # functino to get all environment pk that are not in original sotopia
    env_pks = list(EnvironmentProfile.all_pks())

    return [pk for pk in env_pks if pk not in exclude]


def get_episode_by_env(tag, all_sotopia, all_gen, selected_env=[]):
    # function to select episodes base on environment/scenario pk, as well as tag
    if not selected_env:
        # default to include
        if all_sotopia and all_gen:
            selected_env = list(EnvironmentProfile.all_pks())
        else:
            sotopia_env = get_sotopia_scenarios()
            if all_sotopia:
                selected_env = sotopia_env
            else:
                # if only all gen is True, or nothing is true but no select env is given, use all gen
                selected_env = get_generated_scenarios(sotopia_env)

    # now we have a list of selected env that are not empty
    selected_episodes = {}
    for env in selected_env:
        env_episodes = EpisodeLog.find(EpisodeLog.environment == env).all()
        if tag:
            env_episodes = [
                episode for episode in env_episodes if episode.tag == tag
            ]
        if len(env_episodes) > 0:
            selected_episodes[env] = env_episodes

    return selected_episodes


def align_episode_by_env(episode_list):
    # function to align episodes with its scenarios, result in dic {env: [episodes]}
    env_set = set()
    episode_env_dict: dict[str, list[EpisodeLog]] = {}
    for episode in episode_list:
        env = episode.environment
        if env not in env_set:
            env_set.add(env)
            episode_env_dict[env] = []
        episode_env_dict[env].append(episode)

    return episode_env_dict


def goal_reward_by_env_agent(
    env_epi_dic, reward="goal", filter_threshold=0, balance=False
):
    # function to extract rewards per agent per environment
    # the function could also applied filter and balance two agents' included sets
    reward_dic, filter_dic = {}, {}
    for env, episodes in env_epi_dic.items():
        goal_score = {"agent1": [], "agent2": []}
        env_filter_episodes = {"agent1": [], "agent2": []}
        for episode in episodes:
            rewards = episode.rewards
            if rewards[0] != 0:
                score1 = rewards[0][1][reward]
            else:
                score1 = 0

            if rewards[1] != 0:
                score2 = rewards[1][1][reward]
            else:
                score2 = 0

            # now add based on threshold
            if score1 >= filter_threshold:
                goal_score["agent1"].append(score1)
                env_filter_episodes["agent1"].append(episode.pk)

            if score2 >= filter_threshold:
                goal_score["agent2"].append(score2)
                env_filter_episodes["agent2"].append(episode.pk)

        # if balance, reduce one agent's score to match
        if balance:
            agent1_len, agent2_len = len(goal_score["agent1"]), len(
                goal_score["agent2"]
            )
            if agent1_len != agent2_len:
                target_length = min(agent1_len, agent2_len)
                to_reduce_agent = (
                    "agent1" if agent1_len > target_length else "agent2"
                )
                # reduce agent
                to_reduce_agent_rank = np.argsort(goal_score[to_reduce_agent])[
                    ::-1
                ]
                to_keep_index = to_reduce_agent_rank[:target_length]

                to_keep_score = np.array(goal_score[to_reduce_agent])[
                    to_keep_index
                ].tolist()
                to_keep_episode = np.array(
                    env_filter_episodes[to_reduce_agent]
                )[to_keep_index].tolist()
                goal_score[to_reduce_agent] = to_keep_score
                env_filter_episodes[to_reduce_agent] = to_keep_episode

        reward_dic[env] = goal_score
        filter_dic[env] = env_filter_episodes

    return reward_dic, filter_dic


def filter_pks_to_prompts(filter_env_pks, save_dir, include_format=False):
    # KEY function to run all completion from filter pks
    # function to reverse engineering filter pks, for non-sotopia scenarios
    # here we don't apply scenario filtering for easy-difficult
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for env, agent_dic in filter_env_pks.items():
        for agent, agent_pks in agent_dic.items():
            agent_idx = 0 if agent == "agent1" else 1
            for pk in agent_pks:
                episode = EpisodeLog.get(pk=pk)
                print("This is the episode")
                print(episode)
                parse_prompt_to_json(
                    episode, save_dir, agent_idx, include_format
                )


def get_env_mean_var(env_reward_dic):
    # function to calculate variance and mean of each scenario, each agent
    env_var_dic = {}
    for env, agent_scores in env_reward_dic.items():
        agent_dic = {}
        for agent, scores in agent_scores.items():
            env_var = np.var(scores)
            env_mean = np.mean(scores)
            agent_dic[agent] = {
                "mean": env_mean,
                "var": env_var,
                "count": len(scores),
            }

        env_var_dic[env] = agent_dic

    return env_var_dic


def get_threshold_by_keep_rate(env_rewards, keeprate_, balance=True):
    # function to generate threshold that could use to approximate % of data we want to keep
    keepnum = sum([len(v["agent1"]) for v in env_rewards.values()]) * keeprate_
    keepnum = round(keepnum, 0)  # per agent, keep this many
    scores1 = sum([v["agent1"] for v in env_rewards.values()], [])
    scores2 = sum([v["agent2"] for v in env_rewards.values()], [])
    score1_threshold = np.percentile(scores1, 100 * (1 - keeprate_))
    score2_threshold = np.percentile(scores2, 100 * (1 - keeprate_))

    return (
        max(score1_threshold, score2_threshold)
        if balance
        else min(score1_threshold, score2_threshold)
    )


def get_threshold_by_variance(env_rewards, var_limit, balance=True):
    # function to generate threshold that could use to control the variance

    return


def goal_filter_per_env_agent(episodes, apply_filter=True):
    # function to AUTOMATICALLY filter using goal reward scores for each agent position given scenario
    goal_score = {"agent1": [], "agent2": []}
    env_tpls = []
    # at least need to have half of the total len of the dialogue amount per scenario
    # then add the filtering by score
    if apply_filter:
        min_threshold_amt = len(episodes) // 2
    else:
        min_threshold_amt = -1
    for episode in episodes:
        rewards = episode.rewards
        goal_score["agent1"].append(rewards[0][1]["goal"])
        goal_score["agent2"].append(rewards[1][1]["goal"])

    agent1_avg = np.mean(goal_score["agent1"])
    agent2_avg = np.mean(goal_score["agent2"])
    agent1_rank = np.argsort(goal_score["agent1"])
    agent2_rank = np.argsort(goal_score["agent2"])

    for i in range(len(episodes)):
        # maintain min required # of dialogue for each agent in each scenario
        if i > (min_threshold_amt):
            env_tpls.append((episodes[agent1_rank[i]], 0))
            env_tpls.append((episodes[agent2_rank[i]], 1))
        else:
            if goal_score["agent1"][agent1_rank[i]] >= min(
                GOAL_KEEP_THRESHOD, agent1_avg
            ) and (
                goal_score["agent2"][agent2_rank[i]]
                > min(GOAL_KEEP_THRESHOD, agent2_avg)
            ):
                env_tpls.append((episodes[agent1_rank[i]], 0))
                env_tpls.append((episodes[agent1_rank[i]], 1))

    return env_tpls


def goal_filter_all_env_agent(env_episode_dic, apply_filter=True):
    # aggregate function to AUTOMATICALLY apply filters on all env and episodes in env
    filter_env_dic = {}
    for env, episodes in env_episode_dic.items():
        env_agent_episode = goal_filter_per_env_agent(episodes, apply_filter)
        filter_env_dic[env] = env_agent_episode

    return filter_env_dic


def run_filtered_episodes_to_prompt(
    filter_env_agent_episodes, json_dir, level="Easy", include_format=False
):
    # function to convert selected episode into prompt completion format and save to json
    # use for Sotopia Scenario
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    parse_count = 0
    for env, tpls in filter_env_agent_episodes.items():
        if (level == "Easy" and env in HARD_SCENARIO) or (
            level == "Hard" and env not in HARD_SCENARIO
        ):
            continue
        for tpl in tpls:
            parse_prompt_to_json(tpl[0], json_dir, tpl[1], include_format)
            parse_count += 1

    print(parse_count)


def filter_episodes_to_prompt_main(selected_tag):
    # one shot run of reverse engineering of sotopia scenarios
    episode_by_tag = get_clean_episodes(selected_tag)
    concat_epilist = sum(episode_by_tag.values(), [])
    dic_epi_env = align_episode_by_env(concat_epilist)
    filter_agent_episodes = goal_filter_all_env_agent(dic_epi_env)
    run_filtered_episodes_to_prompt(
        filter_agent_episodes, r"GPT4-4_Redis_Easy"
    )
    run_filtered_episodes_to_prompt(
        filter_agent_episodes, r"GPT4-4_Redis_Hard", "Hard"
    )
