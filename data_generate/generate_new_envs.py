# function to query redis and sample list of unused scenario pks
import os
import sys
import argparse
# this file is used to tranfer data from one redis to another, we do not expect to use it more than once
os.environ[
    "REDIS_OM_URL"
] = "redis://:password@server_name:port_num"

from redis_om import Migrator
from sotopia.database.persistent_profile import (
    AgentProfile,
    EnvironmentProfile,
    RelationshipProfile,
)
from sotopia.database.env_agent_combo_storage import EnvAgentComboStorage
from sotopia.samplers import ConstraintBasedSampler
from sotopia.messages import AgentAction, Observation
from sotopia.agents import LLMAgent
from utils.generate import generate_env_profile

import random
from typing import Any, cast, TypeVar
from tqdm import tqdm
import ast
import pandas as pd
import rich


INSPIRE_PROMPT_FILE = os.getcwd()+"/data_generate/env_files/inspirational_prompt.csv"
USED_PROMPT_FILE = os.getcwd()+"/data_generate/env_files/used_prompt.csv"
USED_ENV_FILE = os.getcwd()+"/data_generate/env_files/used_env.json"

DATASETS = ['normbank', 'social_iqa', 'social_chem']
agent_env_combo_num = 0

def add_env_profile(**kwargs: dict[str, Any]) -> None:
    env_profile = EnvironmentProfile(**kwargs)
    env_profile.save()
    # print("new PK is")
    # print(env_profile.pk)
    return env_profile


def add_env_profiles(env_profiles: list[dict[str, Any]]) -> None:
    env_list = []
    for env_profile in env_profiles:
        profile = add_env_profile(**env_profile)
        env_list.append(profile)
    return env_list


def add_agent_to_database(**kwargs: dict[str, Any]) -> None:
    agent = AgentProfile(**kwargs)
    agent.save()


def add_agents_to_database(agents: list[dict[str, Any]]) -> None:
    for agent in agents:
        add_agent_to_database(**agent)


def retrieve_agent_by_first_name(first_name: str) -> AgentProfile:
    result = AgentProfile.find(AgentProfile.first_name == first_name).all()
    if len(result) == 0:
        raise ValueError(f"Agent with first name {first_name} not found")
    elif len(result) > 1:
        raise ValueError(f"Multiple agents with first name {first_name} found")
    else:
        assert isinstance(result[0], AgentProfile)
        return result[0]
    
    
def add_relationship_profile(**kwargs: dict[str, Any]) -> None:
    relationship_profile = RelationshipProfile(**kwargs)
    relationship_profile.save()


def add_relationship_profiles(
    relationship_profiles: list[dict[str, Any]]
) -> None:
    for relationship_profile in relationship_profiles:
        add_relationship_profile(**relationship_profile)

ENV10 = []
def sample_env_agent_combo_and_push_to_db(env_id: str) -> None:
    sampler = ConstraintBasedSampler[Observation, AgentAction](
        env_candidates=[env_id]
    )
    try:
        env_agent_combo_list = list(
            sampler.sample(agent_classes=[LLMAgent] * 2, replacement=False)
        )
        ENV10.append(env_id)
        #print("Entering here "+env_id)
    except:
        return
    global agent_env_combo_num
    agent_env_combo_num += len(env_agent_combo_list)
    print(agent_env_combo_num)
    for env, agent in env_agent_combo_list:
        EnvAgentComboStorage(
            env_id=env.profile.pk,
            agent_ids=[agent[0].profile.pk, agent[1].profile.pk],
        ).save()

def sample_prompt_by_source(prompt_df, used_prompt, num, source):
    ins_prompts = prompt_df[prompt_df.source == source]
    prompts = [prompt.strip().replace('\"', '') for prompt in ins_prompts["prompt"].tolist()]
    # filter repeated prompts
    prompts = [prompt for prompt in prompts if prompt not in used_prompt] 
    sampled_prompts = [] 
    for i in range(num):
        sampled_prompt = random.sample(prompts, 1)
        sampled_prompts.append(f"{sampled_prompt[0]}")

    return sampled_prompts

def generate_newenv_profile(target_num=500, gen_model="gpt-4-turbo", temperature=0.5):
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
    used_prompts = pd.read_csv(USED_PROMPT_FILE, sep="|")
    used_prompts = used_prompts[used_prompts.model == gen_model].prompt.tolist()
    # filter repeated prompts
    # randomly choose samples
    sampled_examples = []
    for i in range(target_num):
        sampled_envs = random.sample(envs, 1)
        sampled_examples.append(f"{sampled_envs[0].json()}")

    # randomly choose prompts, note we make sure each dataset source has roughly the same amount
    sampled_prompts = []
    subnum = lastnum = target_num // len(DATASETS)
    if subnum*len(DATASETS) < target_num:
        lastnum = target_num-subnum*(len(DATASETS)-1)

    for source in DATASETS[:-1]:
        source_sample = sample_prompt_by_source(ins_prompts, used_prompts, subnum, source)
        sampled_prompts += source_sample
    # the last source could have different number
    sampled_prompts += sample_prompt_by_source(ins_prompts, used_prompts, lastnum, DATASETS[-1])

    assert len(sampled_examples) == target_num
    assert len(sampled_prompts) == target_num

    backgrounds = []
    prompt_sources = []
    for prompt, sampled_example in tqdm(zip(sampled_prompts, sampled_examples), total=target_num):
        rich.print(prompt)
        try:
            background, prompt_full = generate_env_profile(
                    model_name=gen_model,
                    inspiration_prompt=prompt,
                    examples=sampled_example,
                    temperature=temperature,
                )

            assert len(background.agent_goals) == 2

        except Exception as e:
            print(e)
            print('error! Skip')
            # move to next for loop immediately without append
            continue

        #rich.print(background)
        backgrounds.append(background)
        prompt_sources.append(prompt)
    background_df = pd.DataFrame([item.dict() for item in backgrounds])
    # append source
    background_df['prompt'] = pd.DataFrame(prompt_sources)
    background_df['prompt_source'] = background_df.prompt.map(ins_prompts.set_index('prompt')['source'])

    return background_df


def auto_generate_scenarios(num, gen_model="gpt-4-turbo", temperature=0.5):
    """
    Function to generate new environment scenarios based on target number of generation
    """
    all_background_df = generate_newenv_profile(num, gen_model, temperature)
    columns = [ "pk",
                "codename",
                "scenario",
                "agent_goals",
                "relationship",
                "age_constraint",
                "occupation_constraint",
                "source"]
    background_df = all_background_df[columns]
    envs = cast(list[dict[str, Any]], background_df.to_dict(orient="records"))
    filtered_envs = []
    filtered_envs_pks = []
    for env in envs:
        # in case the env["agent_goals"] is string, convert into list
        if isinstance(env["agent_goals"], str):
            env["agent_goals"] = ast.literal_eval(env["agent_goals"])
        assert isinstance(env["relationship"], int)
        if len(env["agent_goals"]) == 2:
            env_pk = env["pk"]
            env.pop("pk")
            filtered_envs.append(env)
            filtered_envs_pks.append(env_pk)
    # add to database
    env_profiles = add_env_profiles(filtered_envs)
    # regardless of error of not, save these prompts as used, 
    # as we don't want to keep error prompts for future use either
    with open(USED_PROMPT_FILE, "a") as use_file:
        #print("writing to file the new propmts")
        for i, new_pk in enumerate(filtered_envs_pks):
            environ = env_profiles[i]
            row = all_background_df[all_background_df.pk == new_pk]
            new_prompt = row.prompt.values[0]
            new_source = row.prompt_source.values[0]
            try:
                use_file.write(gen_model+"|"+str(new_source)+"|"+str(environ.pk)+"|"+new_prompt)
                use_file.write("\n")
            except:
                print(new_source, environ.pk, new_prompt)
    use_file.close()

    # print(env_profiles)
    # also save new combo to database
    for env in env_profiles:
        sample_env_agent_combo_and_push_to_db(env.pk)

    Migrator().run()

    return [envprofile.pk for envprofile in env_profiles]

results = auto_generate_scenarios(24, "gpt-4-turbo", 0.5)
print(len(ENV10))
print(ENV10)
with open("new_env2.txt", 'wb') as f:
    for line in ENV10:
        f.write(line)
        f.write("\n")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--num", type=int,
#                         default=420)
#     parser.add_argument("--gen_model", type=str,
#                         default="gpt-4-turbo")
#     parser.add_argument("--temperature", type=float,
#                         default=0.5)
#     args = parser.parse_args()
#     results = auto_generate_scenarios(args.num, args.gen_model, args.temperature)
#     print("generate newly {} scenarios".format(len(results)))
#     #print(results)

