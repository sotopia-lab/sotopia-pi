deepspeed --num_gpus=1 fastchat/train/train_lora.py \
    --model_name_or_path meta-llama/Llama-2-13b-hf \
    --lora_r 8 \
    --lora_alpha 16 \
    --lora_dropout 0.05 \
    --data_path ./data/fastchat-ft-gpt4-gpt4-easy-2-side-partial.json \
    --shuffle True \
    --bf16 True \
    --output_dir ./checkpoint-shuffle \
    --num_train_epochs 20 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --evaluation_strategy "no" \
    --save_strategy "epoch" \
    --save_total_limit 6 \
    --learning_rate 5e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --model_max_length 2048 \
    --q_lora True \
    --deepspeed ./deepspeed_config_s2.json \
    --hf_access_token "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" \
    --tf32 True \
    --flash_attn True \
    --template "llama-2"

# Possible other options
# --flash_attn True \
# --tf32 True \
# --save_strategy "steps" \ 
# --save_steps 1200 \
# --drop_long_seq True \
# --lazy_preprocess True \