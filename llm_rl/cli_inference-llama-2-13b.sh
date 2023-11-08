python src/cli_demo.py \
    --model_name_or_path meta-llama/Llama-2-13b-hf \
    --cache_dir ./model_cache \
    --template llama2-sotopia \
    --finetuning_type lora \
    --checkpoint_dir /workspace/sotopia-llm/llm_rl/llama2-13b-sft_cache/checkpoint-35