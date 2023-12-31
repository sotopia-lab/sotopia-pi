import argparse
import json
import re
import pandas as pd
from utils.sampling_utils import sample_unused_scenarios


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=str,
                        default="env_files/used_env.json")
    parser.add_argument("--experiment-name", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--show-stat", type=bool, default=False)
    args = parser.parse_args()

    envs = sample_unused_scenarios(
        num=args.num, used_file=args.env_file)

    with open(args.env_file, 'r') as f:
        dic = json.loads(f.read())

    dic[args.experiment_name] = envs

    with open(args.env_file, 'w') as f:
        json_str = json.dumps(dic, indent=4)
        json_str = re.sub(r'\[\s+(.*?)\s+\]', lambda m: '[' +
                          m.group(1).replace('\n', '') + ']', json_str)
        f.write(json_str)

    if args.show_stat:
        df = pd.read_csv("env_files/used_prompt.csv", sep="|")
        selected_rows = df[df["pk"].isin(envs)]
        print(selected_rows["source"].value_counts())


if __name__ == "__main__":
    main()
