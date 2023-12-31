import subprocess
import re
import json
import argparse


def overwrite_eval_bash(
        eval_script: str,
        tag: str,
        env_ids: list,
        batch_size: int = 2,
        agent1_model: str = "gpt-3.5-turbo",
        agent2_model: str = "gpt-3.5-turbo",
        push_to_db: bool = True) -> None:

    with open(eval_script, 'r') as f:
        lines = f.readlines()

    for i in range(len(lines)):
        # change TAG, TAG_TO_CHECK_EXISTING_EPISODES
        if "--gin.TAG_TO_CHECK_EXISTING_EPISODES" in lines[i]:
            pattern = r'(--gin\.TAG_TO_CHECK_EXISTING_EPISODES=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + tag + r'\3', lines[i])
        elif "--gin.TAG" in lines[i]:
            pattern = r'(--gin\.TAG=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + tag + r'\3', lines[i])
        # change ENV_IDS
        elif "--gin.ENV_IDS" in lines[i]:
            pattern = r'(--gin\.ENV_IDS=).*?(\s*\\)'
            lines[i] = re.sub(
                pattern, r'\1' + json.dumps(env_ids) + r"'" + r'\2', lines[i])
        # change batch size
        elif "--gin.BATCH_SIZE" in lines[i]:
            pattern = r'(--gin\.BATCH_SIZE=)(\d+)'
            lines[i] = re.sub(pattern, r'\g<1>' + str(batch_size), lines[i])
        # change agent models
        elif "--gin.AGENT1_MODEL" in lines[i]:
            pattern = r'(--gin\.AGENT1_MODEL=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + agent1_model + r'\3', lines[i])
        elif "--gin.AGENT2_MODEL" in lines[i]:
            pattern = r'(--gin\.AGENT2_MODEL=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + agent2_model + r'\3', lines[i])
        # change push to db flag
        elif "--gin.PUSH_TO_DB" in lines[i]:
            pattern = r'(--gin\.PUSH_TO_DB=)(True|False)'
            lines[i] = re.sub(
                pattern, r'\g<1>' + str(push_to_db), lines[i])

    with open(eval_script, 'w') as f:
        f.write(''.join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-script", type=str, required=True,
                        help="Required. Provide template bash file for sotopia evaluation.")
    parser.add_argument("--env-file", type=str,
                        default="env_files/used_env.json", help="Default: env_files/used_env.json. Provide the json file of env ids for conversation generation.")
    parser.add_argument("--experiment-name", type=str, required=True,
                        help="Required. Need the experiment_name, which is the key of the env_file.")
    parser.add_argument("--tag", type=str, required=True,
                        help="Required. Provide a unique tag that will be pushed to REDIS database.")
    parser.add_argument("--batch-size", type=int, default=2,
                        help="Default: 2. Provide the batch size of calling APIs.")
    parser.add_argument("--agent1-model", type=str, default="gpt-3.5-turbo",
                        help="Default: gpt-3.5-turbo. Provide the name of OPENAI model.")
    parser.add_argument("--agent2-model", type=str, default="gpt-3.5-turbo",
                        help="Default: gpt-3.5-turbo. Provide the name of OPENAI model.")
    parser.add_argument("--push-to-db", type=str, default=True,
                        help="Default: True. If you choose False, then the conversations will not be pushed to REDIS database.")
    args = parser.parse_args()

    with open(args.env_file, 'r') as f:
        env_ids = json.loads(f.read())[args.experiment_name]

    overwrite_eval_bash(eval_script=args.eval_script,
                        tag=args.tag,
                        env_ids=env_ids,
                        batch_size=args.batch_size,
                        agent1_model=args.agent1_model,
                        agent2_model=args.agent2_model,
                        push_to_db=True if args.push_to_db == "True" else False)

    command = f"bash {args.eval_script}"
    subprocess.run(command.split())


if __name__ == "__main__":
    main()
