from pipelines.pull_data import preprocess_episodes_with_tag
from pipelines.run_train import run_sft
from pipelines.monitor_proc import monitor_local_and_upload_to_gcp

import os
import multiprocessing
import yaml

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

def should_stop(run_sft_completed):
    return run_sft_completed.value

def main():
    if not os.path.exists("../llm_rl/data/sotopia_custom_training_sft.json"):
        preprocess_episodes_with_tag()

    for i in range(config["num_improve_steps"]):
        run_sft_completed = multiprocessing.Value('b', False)
        curr_improve_dir = os.path.join(config['data_dir'], config["experiment_name"], f"improve-{i}")
        print(curr_improve_dir)

        sft_process = multiprocessing.Process(target=run_sft, args=(curr_improve_dir, ))
        monitor_process = multiprocessing.Process(target=monitor_local_and_upload_to_gcp, args=(curr_improve_dir, f"{config['experiment_name']}/improve-{i}", 60, lambda: should_stop(run_sft_completed)))
        
        sft_process.start()
        monitor_process.start()
        
        sft_process.join()
        run_sft_completed.value = True
        monitor_process.join()

if __name__ == "__main__":
    main()