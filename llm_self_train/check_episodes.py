import argparse
import json
import os

os.environ["REDIS_OM_URL"] = "redis://:password@server_name:port_num"
from sotopia.database.logs import EpisodeLog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, required=True)
    parser.add_argument("--env-ids", type=str, required=True)
    args = parser.parse_args()

    eps = list(EpisodeLog.find(EpisodeLog.tag == args.tag))
    with open("resources/env_ids.json", "r") as f:
        envs = json.loads(f.read())[args.env_ids]

    for env in envs:
        eps_per_env = list(
            EpisodeLog.find(EpisodeLog.tag == args.tag, EpisodeLog.environment == env)
        )
        print(len(eps_per_env))

    count = 0
    print(len(eps))
    for i in range(len(eps)):
        if eps[i].rewards == [0.0, 0.0]:
            print(i, end=", ")
            count += 1
            EpisodeLog.delete(pk=eps[i].pk)
    print(count)


if __name__ == "__main__":
    main()
