import yaml
import os
import subprocess
import re
import multiprocessing
import time
import json
with open('config/config.yml', 'r') as f:
    config = yaml.safe_load(f)

# log_dir = "/home/ruiyiwan/selftrain_scripts/logs"
# tmp_dir = "/home/ruiyiwan/selftrain_scripts/tmp"
# deploy_model_dir = "/data/tir/projects/tir6/bisk/ruiyiwan/selftrain/pilot-1/"
# generate_gin_file = "/home/ruiyiwan/selftrain_scripts/config/generate.gin"
# deploy_port = 8001
# login_port = 7663
# interval = 60
# user_name = "ruiyiwan"
# deploy_check_max_round = 10


def update_config_yaml(ckpt_name):
    """
    Two global var will be modified: deploy_port and ckpt_name. 
    config['ckpt_name'] = ckpt_name
    config['deploy_port] += 1
    """
    config['deploy_port'] = config['deploy_port'] + 1
    config['ckpt_name'] = ckpt_name

    with open('config/config.yml', 'w') as file:
        yaml.dump(config, file)


def overwrite_deploy_bash():
    """
    The args "--model-path" and "--port" in submit_deploy.sh will be modified.
    """
    with open("submit_deploy.sh", 'r') as f:
        lines = f.readlines()
    with open("submit_deploy.sh", 'w') as f:
        for line in lines:
            if "--model-path" in line:
                line = re.sub(r'--model-path \S+',
                    f'--model-path {os.path.join(config["deploy_model_dir"], config["ckpt_name"])}', line)
            if "--port" in line:
                line = re.sub(r'--port \d+', f'--port {config["deploy_port"]}', line)
            f.write(line)


def overwrite_eval_gin():
    """
    The variables CUSTOM_MODEL_NAME and CUSTOM_OPENAI_API_BASE in generate.gin will be modified.
    """
    with open(config['generate_gin_file'], 'r') as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith('CUSTOM_OPENAI_API_BASE'):
            modified_lines.append(f"""CUSTOM_OPENAI_API_BASE="http://0.0.0.0:{config['deploy_port']}/v1"\n""")
        elif line.startswith('CUSTOM_MODEL_NAME'):
            modified_lines.append(f"""CUSTOM_MODEL_NAME="{config['ckpt_name']}"\n""")
        else:
            modified_lines.append(line)
    
    with open(config['generate_gin_file'], 'w') as f:
        f.writelines(modified_lines)


def generate_gin_tag():
    """
    Generate gin tag based on experiment name, checkpoint name, and agent name
    Example: pilot-1_checkpoint_improve-1_epoch-1_gpt-3.5-turbo_dev
    """
    with open("submit_eval.sh", 'r') as file:
        for line in file:
            if '--gin.AGENT1_MODEL' in line:
                # Extract the value assuming the format '--gin.AGENT1_MODEL="value"'
                parts = re.split(r"[=']", line)
                if len(parts) > 1:
                    # Remove leading and trailing characters like quotes and newline
                    agent1_model = parts[2].strip('"')
                    break
    
    return f"""{config['experiment_name']}_{config['ckpt_name']}_{agent1_model}_dev"""


def overwrite_eval_bash():
    """"""
    with open("submit_eval.sh", 'r') as f:
        lines = f.readlines()

    new_tag = generate_gin_tag()
    for i in range(len(lines)):
        if "--gin.TAG_TO_CHECK_EXISTING_EPISODES" in lines[i]:
            pattern = r'(--gin\.TAG_TO_CHECK_EXISTING_EPISODES=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + new_tag + r'\3', lines[i])
        elif "--gin.TAG" in lines[i]:
            pattern = r'(--gin\.TAG=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + new_tag + r'\3', lines[i])

    # Regex to find '> filename' pattern and replace filename
    lines = ''.join(lines)
    new_filename = f"{config['log_dir']}/eval_status_{config['ckpt_name']}.txt"
    lines = re.sub(r'>(\s*)(\S+)', f'>\\1{new_filename}', lines)
    with open("submit_eval.sh", 'w') as f:
        f.write(lines)


def update_deploy_log():
    # Guaranteed that there is at least one line in the file
    with open(config["deploy_queue_file"], 'r') as f:
        lines = f.readlines()

    with open(config["deploy_queue_file"], 'w') as f:
        if len(lines) == 1:
            pass
        else:
            f.writelines(lines[1:])


def get_deploy_job_id():
    with open(os.path.join(config["tmp_dir"], "deploy_job_id.txt"), 'r') as f:
        line = f.readlines()
        job_id = line[0].split()[3]
    return job_id


def scancel_job(job_id):
    args = f"scancel {job_id}"
    subprocess.run(args.split())


def check_log_and_submit():
    while True:
        # Get queued deploy checkpoint names from deploy_queue.txt
        existing_names = []
        with open(config["deploy_queue_file"], 'r') as f:
            for line in f:
                existing_names.append(line.rstrip())
        # Every 60s find the first checkpoints to be deployed
        if existing_names:
            ckpt_name = existing_names[0]
            # Update config.yml, submit_deploy.sh, generate.gin, submit_eval.sh
            update_config_yaml(ckpt_name)
            overwrite_deploy_bash()
            overwrite_eval_gin()
            overwrite_eval_bash()

            # Submit deploy job
            with open(os.path.join(config["tmp_dir"], "deploy_job_id.txt"), 'w') as f:
                args = f"sbatch --gres=gpu:1 -t 1:00:00 --mem=80g -e {config['log_dir']}/deploy_{config['ckpt_name']}_out.err -o {config['log_dir']}/deploy_{config['ckpt_name']}_out.log submit_deploy.sh"
                subprocess.run(args.split(), stdout=f)
            print(f"Submitted sbatch for deploying {config['ckpt_name']}")
            time.sleep(30)

            # Every 20s, check if deployment is ready, i.e. if the eval monitor signals success or failed
            while True: 
                if os.path.exists(os.path.join(config["log_dir"], f"eval_monitor_fail_{ckpt_name}")):
                    # If deployment is not ready, scancel the deploy job
                    scancel_job(get_deploy_job_id())
                    print(f"Error in deploying. Cancelled {get_deploy_job_id()} and try again...")
                    break
                elif os.path.exists(os.path.join(config["log_dir"], f"eval_monitor_success_{ckpt_name}")):
                    # If the deployment is ready, delete the first row in the deploy queue
                    update_deploy_log()
                    print(f"Running eval on {config['ckpt_name']}")
                    break
                # waiting for eval monitor
                time.sleep(20)

        time.sleep(60)


def main():
    os.umask(0o000)
    if not os.path.exists(config["log_dir"]):
        os.makedirs(config["log_dir"])
        print(f"Creating directory {config['log_dir']}")
    if not os.path.exists(config["tmp_dir"]):
        os.makedirs(config["tmp_dir"])
        print(f"Creating directory {config['tmp_dir']}")
    if not os.path.isfile(config["deploy_queue_file"]):
        with open(config["deploy_queue_file"], 'w') as f:
            pass
            print(f"Deploy queue not found, creating {config['deploy_queue_file']}")
        os.chmod(config["deploy_queue_file"], 0o777)

    monitor_process = multiprocessing.Process(target=check_log_and_submit, args=())
    monitor_process.start()
    monitor_process.join()


if __name__ == "__main__":
    main()