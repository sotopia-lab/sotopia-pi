# Training (BC and/or SR) Pipeline
## Preparations
### Modify `config.yml`
1. Change `experiment_name` and `mkdir experiment_name` in `checkpoint_dir`. Make sure the starting checkpoint and base Mistral model is under `experiment_name` folder.
2. Double-check `checkpoint_saved_queue`.
3. Modify `model_name_or_path` to be the starting checkpoint folder
4. `call_back_save_epoch` control the number of saved checkpoints per improve step.
5. Double-check whether `num_gpus` is the same as the slurm command.
6. Add the env ids for validation in `resources/env_ids.json` and modify `eval_env_ids_tag`.

### Modify `resources/train_args.yml`
1. Upload training dataset to `../llm_rl/data/` and be sure to name the dataset in `../llm_rl/data/dataset_info.json`
2. `cutoff_len` is usually 4096 if we add langchain format.

### (Optional) Modify `resources/deploy_config.yml`

## Run Code
1. Activate conda: `conda activate myenv`
2. Run `python3 monitor_and_submit.py`
2. Open a separate terminal and activate conda. Run `sbatch train.sbatch`


## Comments
1. If you received this error message:
```bash
File "<string>", line 120, in __init__
  File "/home/ruiyiwan/miniconda3/envs/myenv/lib/python3.11/site-packages/transformers/training_args.py", line 1376, in __post_init__
    raise ValueError(
ValueError: Your setup doesn't support bf16/gpu. You need torch>=1.10, using Ampere GPU with cuda>=11.0
```
For non Ampere GPUs, change `bf16: True` to `fp16: True` in `resources/train_args.yml` will solve the error.
