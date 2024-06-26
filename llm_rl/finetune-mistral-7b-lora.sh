deepspeed src/train_bash.py \
    --stage sft \
    --model_name_or_path mistralai/Mistral-7B-v0.1 \
    --dataset sotopia_no_slide_no_filter_format_sft \
    --dataset_dir ./data/ \
    --cutoff_len 4096 \
    --template llama2-sotopia \
    --wandb_project "llama-factory-sft" \
    --wandb_tags "['mistral-7b']" \
    --use_fast_tokenizer False \
    --do_train \
    --num_train_epochs 4.0 \
    --per_device_train_batch_size 8 \
    --gradient_accumulation_steps 2 \
    --finetuning_type lora \
    --lora_target q_proj,v_proj \
    --learning_rate 5e-5 \
    --lr_scheduler_type cosine \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --flash_attn True \
    --gradient_checkpointing True \
    --fp16 True \
    --cache_dir ./model_cache \
    --overwrite_cache \
    --output_dir ./mistral-7b-sft_cache \
    --overwrite_output_dir \
    --logging_steps 1 \
    --save_strategy "epoch" \
    --save_total_limit 5 \
    --use_auth_token True \
    --wandb_token "99caa13ec9552adf0e92e5c30021307ce3cf7fa4" \
    --hf_auth_token "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" \
    --deepspeed ./deepspeed_config_s3.json

    # --dataset alpaca_gpt4_en \
    # --val_size 0.1 \
    # --evaluation_strategy "steps" \
    # --per_device_eval_batch_size 32 \
    # --eval_accumulation_steps 32 \
    # --lora_rank 8 \
    # --lora_alpha 16 \
    # --lora_dropout 0.05 \
