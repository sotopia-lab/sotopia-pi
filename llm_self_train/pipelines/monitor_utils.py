import yaml
import os
import subprocess
import re
import multiprocessing
import time
import json
import shutil
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

log_dir = f"{config['script_dir']}/logs/{config['experiment_name']}"
with open(os.path.join(log_dir, "deploy_config.yml"), 'r') as f:
    deploy_config = yaml.safe_load(f)


# log_dir = "/home/ruiyiwan/selftrain_scripts/logs"
# tmp_dir = "/home/ruiyiwan/selftrain_scripts/tmp"
# deploy_model_dir = "/data/tir/projects/tir6/bisk/ruiyiwan/selftrain/pilot-1/"
# generate_gin_file = "/home/ruiyiwan/selftrain_scripts/config/generate.gin"
# deploy_port = 8001
# login_port = 7663
# interval = 60
# user_name = "ruiyiwan"
# deck_max_round = 10


def update_config_yaml(ckpt_name):
    """
    Two global var will be modified: deploy_port and ckpt_name. 
    config['ckpt_name'] = ckpt_name
    config['deploy_port] += 1
    """
    deploy_config['deploy_port'] = deploy_config['deploy_port'] + 1
    deploy_config['controller_port'] = deploy_config['controller_port'] + 1
    deploy_config['worker_port'] = deploy_config['worker_port'] + 1
    deploy_config['ckpt_name'] = ckpt_name

    with open(os.path.join(log_dir, "deploy_config.yml"), 'w') as file:
        yaml.dump(deploy_config, file)


def overwrite_deploy_bash():
    """
    The args "--model-path" and "--port" in submit_deploy.sh will be modified.
    """
    with open(os.path.join(config["script_dir"], "pipelines", "submit_deploy.sh"), 'r') as f:
        lines = f.readlines()
    with open(os.path.join(config["script_dir"], "pipelines", "submit_deploy.sh"), 'w') as f:
        for line in lines:
            if line.strip().startswith('python3') and 'monitor_deploy_and_run_eval.py' in line:
                line = f"python3 {os.path.join(config['script_dir'], 'pipelines', 'monitor_deploy_and_run_eval.py')} &\n"
            if line.strip().startswith('python3') and 'monitor_eval_and_stop_deploy.py' in line:
                line = re.sub(r'--ckpt-name \S+',
                    f'--ckpt-name {deploy_config["ckpt_name"]}', line)
            if "--model-path" in line:
                line = re.sub(r'--model-path \S+',
                    f'--model-path {os.path.join(config["checkpoint_dir"], config["experiment_name"], deploy_config["ckpt_name"])}', line)
            if "--port" and "fastchat.serve.controller" in line:
                line = re.sub(r'--port \d+', f'--port {deploy_config["controller_port"]}', line)
            if "--port" and "fastchat.serve.model_worker" in line:
                line = re.sub(r'--port \d+', f'--port {deploy_config["worker_port"]}', line)
            if "--port" and "fastchat.serve.openai_api_server" in line:
                line = re.sub(r'--port \d+', f'--port {deploy_config["deploy_port"]}', line)
            if "--worker-address" in line:
                line = re.sub(r'--worker-address \S+',
                    f'--worker-address http://localhost:{deploy_config["worker_port"]}', line)
            if "--controller-address" in line:
                line = re.sub(r'--controller-address \S+',
                    f'--controller-address http://localhost:{deploy_config["controller_port"]}', line)
            f.write(line)


def overwrite_eval_gin():
    """
    The variables CUSTOM_MODEL_NAME and CUSTOM_OPENAI_API_BASE in generate.gin will be modified.
    """
    if not os.path.isfile(os.path.join(log_dir, f"generate_{deploy_config['ckpt_name']}.gin")):
        source_gin_file = "resources/generate.gin"
        shutil.copy(source_gin_file, log_dir+'/'+f"generate_{deploy_config['ckpt_name']}.gin")
        print("Copied generate.gin")

    with open(os.path.join(deploy_config["log_dir"], f"generate_{deploy_config['ckpt_name']}.gin"), 'r') as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith('CUSTOM_OPENAI_API_BASE'):
            modified_lines.append(f"""CUSTOM_OPENAI_API_BASE="http://0.0.0.0:{deploy_config['deploy_port']}/v1"\n""")
        elif line.startswith('CUSTOM_MODEL_NAME'):
            modified_lines.append(f"""CUSTOM_MODEL_NAME="{deploy_config['ckpt_name']}"\n""")
        else:
            modified_lines.append(line)
    
    with open(os.path.join(deploy_config["log_dir"], f"generate_{deploy_config['ckpt_name']}.gin"), 'w') as f:
        f.writelines(modified_lines)


def generate_gin_tag():
    """
    Generate gin tag based on experiment name, checkpoint name, and agent name
    Example: pilot-1_checkpoint_improve-1_epoch-1_gpt-3.5-turbo_dev
    """
    
    with open(os.path.join(log_dir, f"submit_eval_{deploy_config['ckpt_name']}.sh"), 'r') as file:
        for line in file:
            if '--gin.AGENT1_MODEL' in line:
                # Extract the value assuming the format '--gin.AGENT1_MODEL="value"'
                parts = re.split(r"[=']", line)
                if len(parts) > 1:
                    # Remove leading and trailing characters like quotes and newline
                    agent1_model = parts[2].strip('"')
                    break
    
    if config["dev"]:
        return f"""{config['experiment_name']}_{deploy_config['ckpt_name']}_{agent1_model}_dev"""
    return f"""{config['experiment_name']}_{deploy_config['ckpt_name']}_{agent1_model}_test"""


def overwrite_eval_bash():
    """"""
    if not os.path.isfile(os.path.join(log_dir, f"submit_eval_{deploy_config['ckpt_name']}.sh")):
        source_gin_file = "pipelines/submit_eval.sh"
        shutil.copy(source_gin_file, log_dir+'/'+f"submit_eval_{deploy_config['ckpt_name']}.sh")
        print("Copied submit_eval.sh")

    with open(os.path.join(log_dir, f"submit_eval_{deploy_config['ckpt_name']}.sh"), 'r') as f:
        lines = f.readlines()

    new_tag = generate_gin_tag()
    for i in range(len(lines)):
        if "--gin.TAG_TO_CHECK_EXISTING_EPISODES" in lines[i]:
            pattern = r'(--gin\.TAG_TO_CHECK_EXISTING_EPISODES=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + new_tag + r'\3', lines[i])
        elif "--gin.TAG" in lines[i]:
            pattern = r'(--gin\.TAG=")([^"]*)(".*\n)'
            lines[i] = re.sub(pattern, r'\1' + new_tag + r'\3', lines[i])
        elif "--gin_file" in lines[i] and "generate" in lines[i]:
            pattern = r'(--gin_file\s+)([^ ]+)(\s+\\)'
            lines[i] = re.sub(pattern, r'\1' + os.path.join(deploy_config["log_dir"], f"generate_{deploy_config['ckpt_name']}.gin") + r'\3', lines[i])
        elif "--gin.ENV_IDS" in lines[i]:
            # read env_ids.json
            with open(os.path.join(config["script_dir"], "resources", "env_ids.json"), 'r') as f:
                env_ids = json.loads(f.read())[config["eval_env_ids_tag"]]
                env_ids_string = json.dumps(env_ids)
            pattern = r'(--gin\.ENV_IDS=).*?(\s*\\)'
            lines[i] = re.sub(
                pattern, r'\1' + env_ids_string + r"'" + r'\2', lines[i])


    # Regex to find '> filename' pattern and replace filename
    lines = ''.join(lines)
    new_filename = f"{deploy_config['log_dir']}/eval_status_{deploy_config['ckpt_name']}.txt"
    lines = re.sub(r'>(\s*)(\S+)', f'>\\1{new_filename}', lines)
    with open(os.path.join(log_dir, f"submit_eval_{deploy_config['ckpt_name']}.sh"), 'w') as f:
        f.write(lines)


def update_deploy_log():
    # Guaranteed that there is at least one line in the file
    with open(config["checkpoint_saved_queue"], 'r') as f:
        lines = f.readlines()

    with open(config["checkpoint_saved_queue"], 'w') as f:
        if len(lines) == 1:
            pass
        else:
            f.writelines(lines[1:])


def get_deploy_job_id():
    with open(os.path.join(deploy_config["tmp_dir"], "deploy_job_id.txt"), 'r') as f:
        line = f.readlines()
        job_id = line[0].split()[3]
    return job_id


def scancel_job(job_id):
    args = f"scancel {job_id}"
    subprocess.run(args.split())


def map_ckpt_to_job(job_id):
    if not os.path.isfile(os.path.join(deploy_config['tmp_dir'], "map_ckpt_job.txt")):
        lines = []
    else:
        with open(os.path.join(deploy_config['tmp_dir'], "map_ckpt_job.txt"), 'r') as f:
            lines = f.readlines()
    new_line = f"{deploy_config['ckpt_name']}:{job_id}\n"
    lines.append(new_line)
    with open(os.path.join(deploy_config['tmp_dir'], "map_ckpt_job.txt"), 'w') as f:
        f.writelines(lines)


def save_gin_tag():
    lines = []
    if os.path.isfile(os.path.join(deploy_config['tmp_dir'], "generate_tags.txt")):
        with open(os.path.join(deploy_config['tmp_dir'], "generate_tags.txt"), 'r') as f:
            lines = f.readlines()
    lines.append(f"{deploy_config['ckpt_name']}:{generate_gin_tag()}\n")

    with open(os.path.join(deploy_config['tmp_dir'], "generate_tags.txt"), 'w') as f:
        f.writelines(lines)


def check_log_and_submit_deploy():
    while True:
        # Get queued deploy checkpoint names from deploy_queue.txt
        existing_names = []
        with open(config["checkpoint_saved_queue"], 'r') as f:
            for line in f:
                existing_names.append(line.rstrip())
        # Every 60s find the first checkpoints to be deployed
        if existing_names:
            ckpt_name = existing_names[0]
            # in case the line is empty
            if len(ckpt_name) < 2:
                time.sleep(60)
                continue
            # Update config.yml, submit_deploy.sh, generate.gin, submit_eval.sh
            update_config_yaml(ckpt_name)
            overwrite_deploy_bash()
            overwrite_eval_gin()
            overwrite_eval_bash()

            # Submit deploy job
            with open(os.path.join(deploy_config["tmp_dir"], "deploy_job_id.txt"), 'w') as f:
                args = f"sbatch --gres=gpu:1 -t 12:00:00 --mem=80g --exclude=shire-1-6,babel-8-19,babel-7-37 -e {deploy_config['log_dir']}/deploy_{deploy_config['ckpt_name']}_out.err -o {deploy_config['log_dir']}/deploy_{deploy_config['ckpt_name']}_out.log {config['script_dir']}/pipelines/submit_deploy.sh"
                subprocess.run(args.split(), stdout=f)
            print(f"Submitted sbatch for deploying {deploy_config['ckpt_name']}")

            # Update map for scanceling deploy job by monitor_eval_and_stop_deploy.py
            map_ckpt_to_job(get_deploy_job_id())
            time.sleep(30)

            # Every 20s, check if deployment is ready, i.e. if the eval monitor signals success or failed
            while True: 
                if os.path.exists(os.path.join(deploy_config["log_dir"], f"eval_monitor_fail_{deploy_config['ckpt_name']}")):
                    # If deployment is not ready, scancel the deploy job
                    scancel_job(get_deploy_job_id())
                    print(f"Error in deploying. Cancelled {get_deploy_job_id()} and try again...")
                    os.remove(os.path.join(deploy_config["log_dir"], f"eval_monitor_fail_{deploy_config['ckpt_name']}"))
                    break
                elif os.path.exists(os.path.join(deploy_config["log_dir"], f"eval_monitor_success_{deploy_config['ckpt_name']}")):
                    # If the deployment is ready, delete the first row in the deploy queue
                    update_deploy_log()
                    print(f"Running eval on {deploy_config['ckpt_name']}")
                    # Save generate.gin tag for future evaluation
                    save_gin_tag()
                    break
                # waiting for eval monitor
                time.sleep(20)

        time.sleep(60)



def check_log_and_cancel_deploy():
    # Every 120s, check scancel list
    while True:
        if not os.path.isfile(os.path.join(deploy_config["tmp_dir"], "scancel_list.txt")):
            with open(os.path.join(deploy_config["tmp_dir"], "scancel_list.txt"), 'w') as f:
                pass
        with open(os.path.join(deploy_config["tmp_dir"], "scancel_list.txt"), 'r') as f:
            lines = f.readlines()

        if len(lines) > 0:
            for line in lines:
                job_id = line.strip()
                scancel_job(job_id)
                print(f"Eval finished. Scancelled job {job_id}")

        with open(os.path.join(deploy_config["tmp_dir"], "scancel_list.txt"), 'w') as f:
            f.writelines([])
                

        time.sleep(60)
