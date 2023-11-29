from pipelines.pull_data import preprocess_episodes_with_tag
from pipelines.run_train import run_sft
from pipelines.gcp_util import monitor_and_upload

import asyncio
import os


def main():
    if not os.path.exists("../llm_rl/data/sotopia_custom_training_sft.json"):
        preprocess_episodes_with_tag()
        
    global run_sft_completed
    run_sft_completed = False
    
    asyncio.run(monitor_and_upload("./output_cache", 5))
    run_sft()
    run_sft_completed = True
    
    
if __name__ == "__main__":
    main()