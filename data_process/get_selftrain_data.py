import sys
import os
os.environ[
    "REDIS_OM_URL"
] = "redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"

import json
import argparse
from sotopia.database.logs import EpisodeLog
from rich.terminal_theme import MONOKAI 
from utils.prompt_reverse_engineering import reverse_episode_log


def get_episodes_by_env_dict(
    tags: list, 
    scenarios: set,
) -> dict[str, list[EpisodeLog]]:
     # Load all episodes from tags
    eps_by_tag = {}
    for tag in tags:
        eps = EpisodeLog.find(EpisodeLog.tag == tag).all()
        if len(eps) > 0:
            eps_by_tag[tag] = eps
    eps_list = sum(eps_by_tag.values(), [])

    # Only select episodes under target scenarios
    eps_by_env = {}
    for ep in eps_list:
        if ep.environment in scenarios:
            if ep.environment in eps_by_env:
                eps_by_env[ep.environment].append(ep)
            else:
                eps_by_env[ep.environment] = [ep]
    
    return eps_by_env


def get_sorted_episode_list_for_target_agent(
    tags: list, 
    scenarios: set,
    agent_model: str,
    reward_metric: str = "overall_score"
) -> list:
    
    eps_by_env = get_episodes_by_env_dict(tags, scenarios)
    eps_list = sum(eps_by_env.values(), [])
    
    # Split into two cases where the target agent converses with another agent or itself
    single_agent_eps_list = []
    dual_agent_1_eps_list = []
    dual_agent_2_eps_list = []
    for ep in eps_list:
        if ep.models[1] == agent_model and ep.models[2] == agent_model:
            dual_agent_1_eps_list.append((1, ep))
            dual_agent_2_eps_list.append((2, ep))
        elif ep.models[1] == agent_model or ep.models[2] == agent_model:
            single_agent_eps_list.append((0, ep))

    combined_eps_list = single_agent_eps_list + dual_agent_1_eps_list + dual_agent_2_eps_list

    def reward_sort_fn(x):
        if x[0] == 0:
            return x[1].rewards[0][1][reward_metric] if x[1].models[1] == agent_model else x[1].rewards[1][1][reward_metric]
        elif x[0] == 1:
            return x[1].rewards[0][1][reward_metric]
        else:
            return x[1].rewards[1][1][reward_metric]
        
    sorted_combined_eps_list = sorted(combined_eps_list, key=reward_sort_fn, reverse=True)

    return sorted_combined_eps_list


def select_top_reward_eps(
    sorted_eps_list: list,
    ratio: float = 0.7
) -> list:
    return sorted_eps_list[:round(ratio * len(sorted_eps_list))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file")