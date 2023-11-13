CUDA_VISIBLE_DEVICES=0 python src/train_bash.py \
    --stage ppo \
    --model_name_or_path mistralai/Mistral-7B-v0.1 \
    --do_train \
    --dataset alpaca_gpt4_en \
    --template default \
    --finetuning_type lora \
    --lora_target q_proj,v_proj \
    --resume_lora_training False \
    --checkpoint_dir /workspace/sotopia-llm/llm_rl/mistral-7b-sft_cache/checkpoint-10 \
    --reward_model /workspace/sotopia-llm/llm_rl/mistral-7b-rm_cache/checkpoint-10 \
    --cache_dir ./model_cache \
    --overwrite_cache \
    --output_dir ./mistral-7b-ppo_cache \
    --overwrite_output_dir \
    --per_device_train_batch_size 2 \
    --gradient_accumulation_steps 4 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate 1e-5 \
    --num_train_epochs 1.0 \
    --plot_loss \
    --bf16 

