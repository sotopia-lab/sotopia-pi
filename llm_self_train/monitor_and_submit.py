import json
import multiprocessing
import os
import re
import shutil
import subprocess
import time

import yaml

os.umask(0o000)

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)


log_dir = f"{config['script_dir']}/logs/{config['experiment_name']}"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    print(f"Created directory {log_dir}")

if not os.path.isfile(os.path.join(log_dir, "deploy_config.yml")):
    source_deploy_file = "resources/deploy_config.yml"
    shutil.copy(source_deploy_file, log_dir + "/")
    print("Copied deploy_config.yml")


with open(os.path.join(log_dir, "deploy_config.yml"), "r") as f:
    deploy_config = yaml.safe_load(f)

deploy_config["log_dir"] = log_dir
deploy_config["tmp_dir"] = f"{config['script_dir']}/tmp/{config['experiment_name']}"

with open(os.path.join(log_dir, "deploy_config.yml"), "w") as f:
    yaml.dump(deploy_config, f)

from pipelines.monitor_utils import (
    check_log_and_cancel_deploy,
    check_log_and_submit_deploy,
)


def main():
    if not os.path.exists(deploy_config["tmp_dir"]):
        os.makedirs(deploy_config["tmp_dir"])
        print(f"Created directory {deploy_config['tmp_dir']}")
    if not os.path.isfile(config["checkpoint_saved_queue"]):
        with open(config["checkpoint_saved_queue"], "w") as f:
            pass
            print(f"Deploy queue not found, created {config['checkpoint_saved_queue']}")
        os.chmod(config["checkpoint_saved_queue"], 0o777)

    submit_monitor_process = multiprocessing.Process(
        target=check_log_and_submit_deploy, args=()
    )
    cancel_monitor_process = multiprocessing.Process(
        target=check_log_and_cancel_deploy, args=()
    )
    submit_monitor_process.start()
    cancel_monitor_process.start()
    submit_monitor_process.join()
    cancel_monitor_process.join()


if __name__ == "__main__":
    main()
