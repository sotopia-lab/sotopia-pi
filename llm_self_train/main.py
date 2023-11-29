import os
from pipelines.pull_data import preprocess_episodes_with_tag
from pipelines.run_train import run_sft


def main():
    if not os.path.exists("../llm_rl/data/sotopia_custom_training_sft.json"):
        preprocess_episodes_with_tag()
    run_sft()
    
if __name__ == "__main__":
    main()