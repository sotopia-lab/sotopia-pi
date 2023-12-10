from pipelines.pull_data import preprocess_episodes_with_tag
from pipelines.run_train import run_sft
from pipelines.monitor_proc import monitor_local_and_upload_to_gcp

import os
import multiprocessing
import time

def should_stop(run_sft_completed):
    return run_sft_completed.value

def timer(timeout, run_sft_completed):
    time.sleep(timeout)
    print("Stopping...")
    run_sft_completed.value = True

def main():
    if not os.path.exists("../llm_rl/data/sotopia_custom_training_sft.json"):
        preprocess_episodes_with_tag()
        
    run_sft_completed = multiprocessing.Value('b', False)
    
    sft_process = multiprocessing.Process(target=run_sft)
    
    monitor_process = multiprocessing.Process(target=monitor_local_and_upload_to_gcp, args=("./output_cache", "./Improve-3", 60, lambda: should_stop(run_sft_completed)))
    
    timer_process = multiprocessing.Process(target=timer, args=(60*20, run_sft_completed))
    
    sft_process.start()
    monitor_process.start()
    timer_process.start()
    
    sft_process.join()
    monitor_process.join()
    timer_process.join()
    
    
if __name__ == "__main__":
    main()