CUDA_VISIBLE_DEVICES=0 python src/train_bash.py \
    --stage rm \
    --model_name_or_path meta-llama/Llama-2-13b-hf \
    --do_train \
    --dataset comparison_gpt4_en \
    --template default \
    --finetuning_type lora \
    --lora_target q_proj,v_proj \
    --resume_lora_training False \
    --output_dir ./llama-2-13b-rm_cache \
    --per_device_train_batch_size 8 \
    --gradient_accumulation_steps 8 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate 1e-6 \
    --num_train_epochs 1.0 \
    --plot_loss \
    --fp16 \
    --use_auth_token True \
    --wandb_token "99caa13ec9552adf0e92e5c30021307ce3cf7fa4" \
    --hf_auth_token "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" \
    --deepspeed ./deepspeed_config_s2.json
