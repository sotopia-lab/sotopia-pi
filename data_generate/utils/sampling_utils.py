# function to query redis and sample list of unused scenario pks
import os
import sys

# this file is used to tranfer data from one redis to another, we do not expect to use it more than once
os.environ["REDIS_OM_URL"] = "redis://:password@server_name:port_num"

import json
import random

from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import EnvironmentProfile


def get_sotopia_scenarios():
    """
    Function to get all sotopia scenario pk
    """
    # function to get all sotopia scenario pk
    # we use gpt4-gpt4 tag to collect all sotopia scenario, other clean tags should do the same thing
    tag = "gpt-4_gpt-4_v0.0.1_clean"
    tag_epis = EpisodeLog.find(EpisodeLog.tag == tag).all()
    sotopia_env_pk = set([episode.environment for episode in tag_epis])
    return list(sotopia_env_pk)


def get_used_env(filename, key=None):
    """
    Function that retrieve so far used environment profile to avoid repetitively generate data
    using the same environment profile
    Args:
        filename: path to the json file that saved so-far-used pks
        key: optional, as in each experiment, we would save a different list of pks
    """
    with open(filename, "r") as file:
        used_dic = json.load(file)
    if not key:
        return sum(used_dic.values(), [])
    else:
        return used_dic[key]


def sample_unused_scenarios(num, used_file, experiment_name=None):
    """
    Function that automatically generate data -- main runner function
    The logic is as follow:
        For unused environment that are not in SOTOPIA, we sample list of envs based on num to sample
        If we have enough unsed pks, then we sample all pks and return a list
        If we don't have enough, go to auto generate that amount of scenarios, and then return

    """
    used_pks = get_used_env(used_file, key=experiment_name)
    sotopia_envs = get_sotopia_scenarios()

    used_pks += sotopia_envs
    # retrieve from redis DB the number of scenarios
    env_pks = set(EnvironmentProfile.all_pks())
    # take un-overlapping portion
    candidates = list(set(used_pks) ^ env_pks)
    samples = random.sample(candidates, num)
    # else:
    #     new_pks = auto_generate_scenarios(num)
    #     samples = random.sample(candidates+new_pks, num)

    return samples
