import yaml
import os
import subprocess
import re
import multiprocessing
import time
import json
from pipelines.monitor_utils import check_log_and_submit_deploy, check_log_and_cancel_deploy

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

with open("resources/deploy_config.yml", 'r') as f:
    deploy_config = yaml.safe_load(f)

deploy_config['log_dir'] = f"{config['script_dir']}/logs/{config['experiment_name']}"
deploy_config['tmp_dir'] = f"{config['script_dir']}/tmp/{config['experiment_name']}"

with open('resources/deploy_config.yml', 'w') as f:
    yaml.dump(deploy_config, f)


def main():
    os.umask(0o000)
    if not os.path.exists(deploy_config["log_dir"]):
        os.makedirs(deploy_config["log_dir"])
        print(f"Created directory {deploy_config['log_dir']}")
    if not os.path.exists(deploy_config["tmp_dir"]):
        os.makedirs(deploy_config["tmp_dir"])
        print(f"Created directory {deploy_config['tmp_dir']}")
    if not os.path.isfile(config["checkpoint_saved_queue"]):
        with open(config["checkpoint_saved_queue"], 'w') as f:
            pass
            print(f"Deploy queue not found, created {config['checkpoint_saved_queue']}")
        os.chmod(config["checkpoint_saved_queue"], 0o777)

    submit_monitor_process = multiprocessing.Process(target=check_log_and_submit_deploy, args=())
    cancel_monitor_process = multiprocessing.Process(target=check_log_and_cancel_deploy, args=())
    submit_monitor_process.start()
    cancel_monitor_process.start()
    submit_monitor_process.join()
    cancel_monitor_process.join()


if __name__ == "__main__":
    main()