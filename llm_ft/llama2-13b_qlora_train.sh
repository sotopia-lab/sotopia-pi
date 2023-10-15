deepspeed fastchat/train/train_lora.py \
    --model_name_or_path meta-llama/Llama-2-13b-chat-hf \
    --lora_r 8 \
    --lora_alpha 16 \
    --lora_dropout 0.05 \
    --data_path ./data/dummy_convs_haofei.json \
    --shuffle False \
    --bf16 True \
    --output_dir ./checkpoint \
    --num_train_epochs 2 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 8 \
    --evaluation_strategy "no" \
    --save_strategy "epoch" \
    --save_total_limit 6 \
    --learning_rate 5e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --tf32 True \
    --model_max_length 2048 \
    --q_lora True \
    --deepspeed ./deepspeed_config.json \
    --hf_access_token "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"

# Possible other options
# --save_strategy "steps" \ 
# --save_steps 1200 \