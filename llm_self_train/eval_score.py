import argparse
import os

os.environ["REDIS_OM_URL"] = "redis://:password@server_name:port_num"
import json

import numpy as np
from sotopia.database.logs import EpisodeLog
from sotopia.database.persistent_profile import (
    AgentProfile,
    EnvironmentProfile,
)

# tag = "pilot-2_checkpoint_improve-0_epoch-3_gpt-3.5-turbo_dev"
# target_model = "custom_model"

# hard_envs = ["01HJPQ34Y3S1TDPTRX1CCH6VPG", "01HJPQ34ZG9WZEDX6BV5QZB1QG"]


def gen_target_result_dict(envs: list, tag: str, target_model: str) -> dict:
    target_result_by_env = []
    for env_profile_id in envs:

        env = EnvironmentProfile.get(env_profile_id)
        target_result_dict = {
            "env_profile_id": env_profile_id,
            "scenario": env.scenario,
            "target_as_agent_1": {},
            "target_as_agent_2": {},
        }

        target_result_dict["target_as_agent_1"] = {
            "agent_env_goal": env.agent_goals[0],
            "agent_performance_by_profile": [],
        }

        target_result_dict["target_as_agent_2"] = {
            "agent_env_goal": env.agent_goals[1],
            "agent_performance_by_profile": [],
        }

        eps = list(
            EpisodeLog.find(
                EpisodeLog.tag == tag, EpisodeLog.environment == env_profile_id
            )
        )

        for i in range(len(eps)):
            if eps[i].models[1] == target_model:  # target as agent 1

                agent_id = eps[i].agents[0]
                agent_profile = list(AgentProfile.find(AgentProfile.pk == agent_id))[0]
                agent_first_name, agent_last_name = (
                    agent_profile.first_name,
                    agent_profile.last_name,
                )
                agent_performance_dict = {
                    "agent_profile_id": agent_id,
                    "agent_first_name": agent_first_name,
                    "agent_last_name": agent_last_name,
                    "reward": eps[i].rewards[0],
                    "reasoning": eps[i].reasoning,
                }
                target_result_dict["target_as_agent_1"][
                    "agent_performance_by_profile"
                ].append(agent_performance_dict)

            if eps[i].models[2] == target_model:
                agent_id = eps[i].agents[1]
                agent_profile = list(AgentProfile.find(AgentProfile.pk == agent_id))[0]
                agent_first_name, agent_last_name = (
                    agent_profile.first_name,
                    agent_profile.last_name,
                )
                agent_performance_dict = {
                    "agent_profile_id": agent_id,
                    "agent_first_name": agent_first_name,
                    "agent_last_name": agent_last_name,
                    "reward": eps[i].rewards[1],
                    "reasoning": eps[i].reasoning,
                }
                target_result_dict["target_as_agent_2"][
                    "agent_performance_by_profile"
                ].append(agent_performance_dict)

        target_result_by_env.append(target_result_dict)

    return target_result_by_env


def eval_average(target_result_by_env: dict, tag: str) -> dict:
    avg_dict = {
        "believability": 0.0,
        "relationship": 0.0,
        "knowledge": 0.0,
        "secret": 0.0,
        "social_rules": 0.0,
        "financial_and_material_benefits": 0.0,
        "goal": 0.0,
        "overall_score": 0.0,
    }

    eps = list(EpisodeLog.find(EpisodeLog.tag == tag))

    for result_dict in target_result_by_env:
        for key in avg_dict:
            if (
                len(result_dict["target_as_agent_1"]["agent_performance_by_profile"])
                == 0
            ):
                perf_as_agent_1 = 0
            else:
                perf_as_agent_1 = np.sum(
                    [
                        agent_profile["reward"][1][key]
                        for agent_profile in result_dict["target_as_agent_1"][
                            "agent_performance_by_profile"
                        ]
                    ]
                )
            if (
                len(result_dict["target_as_agent_2"]["agent_performance_by_profile"])
                == 0
            ):
                perf_as_agent_2 = 0
            else:
                perf_as_agent_2 = np.sum(
                    [
                        agent_profile["reward"][1][key]
                        for agent_profile in result_dict["target_as_agent_2"][
                            "agent_performance_by_profile"
                        ]
                    ]
                )
            # print(len(result_dict["target_as_agent_1"]["agent_performance_by_profile"]))
            # print(len(result_dict["target_as_agent_2"]["agent_performance_by_profile"]))
            # avg_dict[key] += (perf_as_agent_1 + perf_as_agent_2) / 2 / len(target_result_by_env)
            avg_dict[key] += (perf_as_agent_1 + perf_as_agent_2) / len(eps)
            # avg_dict[key] += (perf_as_agent_1 + perf_as_agent_2) / 14

    return avg_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, required=True)
    parser.add_argument("--target-model", type=str, default="custom_model")
    parser.add_argument("--env-ids-tag", type=str, required=True)
    parser.add_argument("--out-dir", type=str, required=True)
    args = parser.parse_args()

    with open("resources/env_ids.json", "r") as f:
        env_dict = json.loads(f.read())
    envs = env_dict[args.env_ids_tag]

    target_result_by_env = gen_target_result_dict(
        envs=envs, target_model=args.target_model, tag=args.tag
    )

    avg_dict = eval_average(target_result_by_env, tag=args.tag)

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)
    with open(os.path.join(args.out_dir, f"{args.tag}.json"), "w") as f:
        f.write(json.dumps(avg_dict, indent=4))
    with open(os.path.join(args.out_dir, f"dict.json"), "w") as f:
        f.write(json.dumps(target_result_by_env, indent=4))


if __name__ == "__main__":
    main()
