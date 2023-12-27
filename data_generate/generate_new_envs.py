# function to query redis and sample list of unused scenario pks
import os
import sys
# this file is used to tranfer data from one redis to another, we do not expect to use it more than once
os.environ[
    "REDIS_OM_URL"
] = "redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"

from redis_om import Migrator
from sotopia.database.logs import EpisodeLog
import json
from sotopia.database.persistent_profile import EnvironmentProfile
from step2_push_agent_relationship_env_to_db import add_env_profiles, sample_env_agent_combo_and_push_to_db
from generate import generate_env_profile

import random
from typing import Any, cast, TypeVar
from tqdm import tqdm
import ast
import pandas as pd
import rich
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
INSPIRE_PROMPT_FILE = os.getcwd()+"/data_generate/env_files/inspirational_prompt.csv"
USED_PROMPT_FILE = os.getcwd()+"/data_generate/env_files/used_prompt.csv"
USED_ENV_FILE = os.getcwd()+"/data_generate/env_files/used_env.json"


def generate_newenv_profile(target_num=500, gen_model="gpt-4-turbo"):
    """
    Function to generate new environment profile
    Args:
        target_num: how many new environment profile is targeted
        gen_model: default to GPT4 model, but should allow other model input
    """
    envs = EnvironmentProfile.find().all()
    # this two lists should be kept as 
    # 1. source/pool of prompts 
    # 2. tracker for previously used prompts
    ins_prompts = pd.read_csv(INSPIRE_PROMPT_FILE)
    used_prompts = pd.read_csv(USED_PROMPT_FILE)
    used_prompts = used_prompts[used_prompts.model == gen_model].prompt.tolist()
    prompts = [prompt.strip().replace('\"', '') for prompt in ins_prompts["prompt"].tolist()]
    # filter repeated prompts
    prompts = [prompt for prompt in prompts if prompt not in used_prompts]
    # randomly choose prompts
    sampled_examples = []
    sampled_prompts = []
        
    for i in range(target_num):
        sampled_envs = random.sample(envs, 1)
        sampled_prompt = random.sample(prompts, 1)
        sampled_examples.append(f"{sampled_envs[0].json()}")
        sampled_prompts.append(f"{sampled_prompt[0]}")

    assert len(sampled_examples) == target_num
    assert len(sampled_prompts) == target_num

    backgrounds = []
    for prompt, sampled_example in tqdm(zip(sampled_prompts, sampled_examples), total=target_num):
        rich.print(prompt)
        try:
            background, prompt_full = generate_env_profile(
                    model_name=gen_model,
                    inspiration_prompt=prompt,
                    examples=sampled_example,
                    temperature=0.5,
                )

            assert len(background.agent_goals) == 2
        except Exception as e:
            print(e)
            print('error! Skip')
            continue

        #rich.print(background)
        backgrounds.append(background)
    background_df = pd.DataFrame([item.dict() for item in backgrounds])
    # regardless of error of not, save these prompts as used, 
    # as we don't want to keep error prompts for future use either
    with open(USED_PROMPT_FILE, "a") as use_file:
        #print("writing to file the new propmts")
        for new_prompt in sampled_prompts:
            use_file.write(new_prompt+","+gen_model)
            use_file.write("\n")
    use_file.close()

    return background_df


def auto_generate_scenarios(num):
    """
    Function to generate new environment scenarios based on target number of generation
    """
    background_df = generate_newenv_profile(num)
    columns = ["codename",
                "scenario",
                "agent_goals",
                "relationship",
                "age_constraint",
                "occupation_constraint",
                "source"]
    background_df = background_df[columns]
    envs = cast(list[dict[str, Any]], background_df.to_dict(orient="records"))
    filtered_envs = []
    for env in envs:
        # in case the env["agent_goals"] is string, convert into list
        if isinstance(env["agent_goals"], str):
            env["agent_goals"] = ast.literal_eval(env["agent_goals"])
        assert isinstance(env["relationship"], int)
        if len(env["agent_goals"]) == 2:
            filtered_envs.append(env)
    # add to database
    env_profiles = add_env_profiles(envs)
    # print(env_profiles)
    # also save new combo to database
    for env in env_profiles:
        sample_env_agent_combo_and_push_to_db(env.pk)

    Migrator().run()

    return [envprofile.pk for envprofile in env_profiles]