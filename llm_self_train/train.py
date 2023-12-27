from pipelines.pull_data import preprocess_episodes_with_tag
from pipelines.run_train import run_sft
from llm_self_train.pipelines.monitor_processes import monitor_local_and_upload_to_gcp

import os
import multiprocessing
import yaml

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)


def should_stop(run_sft_completed):
    return run_sft_completed.value

def main():
    os.umask(0o000)

    if not os.path.exists("../llm_rl/data/sotopia_custom_training_sft.json"):
        preprocess_episodes_with_tag()

    for improve_step in range(config["num_improve_steps"]):
        run_sft_completed = multiprocessing.Value('b', False)
        output_dir = os.path.join(config['data_dir'], config["experiment_name"])
        sft_process = multiprocessing.Process(target=run_sft, args=(output_dir, improve_step, ))
        sft_process.start()
        sft_process.join()

        run_sft_completed.value = True
        
if __name__ == "__main__":
    main()