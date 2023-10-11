We need to use an unmerged branch to support deploying lora-finetuned model. (the forked repo is https://github.com/troph-team/vllm.git)

Go to the vllm dir and pip install -e .

To notice https://github.com/vllm-project/vllm/issues/1283, need to modify the config file to == 2.0.1 and the pytorch version if facing with CUDA version error.