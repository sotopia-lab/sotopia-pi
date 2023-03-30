# FastChat
An open platform for training, serving, and evaluating large language model based chatbots.

## Release
- 🔥 We released **Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90% ChatGPT Quality**. Checkout the blog [post]() and [demo]().


<!-- ![demo](assets/demo-narrow.gif) -->
<a href="https://chat.lmsys.org"><img src="assets/demo-narrow.gif" width="70%"></a>


Join our [Discord]() server and follow our [Twitter]() to get the latest updates.

## Contents
- [Install](#install)
- [Serving](#serving)
- [Fine-tuning](#fine-tuning)
- [Evaluation](#evaluation)

## Install

### Method 1: From Source
```
git clone https://github.com/lm-sys/FastChat.git
cd FastChat
pip3 install -e .

# Install the latest main branch of huggingface/transformers
pip3 install git+https://github.com/huggingface/transformers
```

## Serving

### Command Line Interface
```
python3 -m fastchat.serve.cli --model facebook/opt-1.3b
```

### Web UI
```
# Launch a controller
python3 -m fastchat.serve.controller

# Launch a model worker
python3 -m fastchat.serve.model_worker --model-path facebook/opt-1.3b

# Send a test message
python3 -m fastchat.serve.test_message

# Luanch a gradio web server.
python3 -m fastchat.serve.gradio_web_server

# You can open your brower and chat with a model now.
```

## Fine-tuning


### Data

Vicuna is created by fine-tuning a LLaMA base model using approximately 70K user-shared conversations gathered from ShareGPT.com with public APIs. To ensure data quality, we convert the HTML back to markdown and filter out some inappropriate or low-quality samples. Additionally, we divide lengthy conversations into smaller segments that fit the model's maximum context length.

Due to the legal concerns, we may not release the data at the moment. If you would like to try the fine-tuning code, you can try to run it with our [preprocessed alpaca dataset](playground/data/alpaca-data-conversation.json) (originally from [here](https://github.com/tatsu-lab/stanford_alpaca)).

### Code and Hyperparameters
We fine-tune the model using the code from [Stanford Alpaca](https://github.com/tatsu-lab/stanford_alpaca), with some modifications to support gradient checkpointing and [Flash Attention](https://github.com/HazyResearch/flash-attention). We use the similar hyperparameters as the Stanford Alpaca.

| Hyperparameter | Global Batch Size | Learning rate | Epochs | Max length | Weight decay |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vicuna-13B | 128 | 2e-5 | 3 | 2048 | 0 |

### Fine-tuning on Any Cloud with SkyPilot
[SkyPilot](https://github.com/skypilot-org/skypilot) is a framework built by UC Berkeley for easily and cost effectively running ML workloads on any cloud. 
To use SkyPilot, install it with the following command and setup the cloud credentials locally following the instructions [here](https://skypilot.readthedocs.io/en/latest/getting-started/installation.html).
```bash
# Install skypilot from the master branch
pip install git+https://github.com/skypilot-org/skypilot.git
```
#### Vicuna
Vicuna can be trained on 8 A100 GPUs with 80GB memory. The following command will automatically launch a node satisfying the requirement, setup and run the training job on it.
```bash
sky launch -c vicuna -s scripts/train-vicuna.yaml --env WANDB_API_KEY
```
Other options are also valid:
```bash
# Launch it on managed spot to save 3x cost
sky spot launch -n vicuna scripts/train-vicuna.yaml --env WANDB_API_KEY

# Train a 7B model
sky launch -c vicuna -s scripts/train-vicuna.yaml --env WANDB_API_KEY --env MODEL_SIZE=7
```
Note: Please make sure the `WANDB_API_KEY` has been setup on your local machine. You can find the API key on your [wandb profile page](https://wandb.ai/authorize). If you would like to train the model without using wandb, you can replace the `--env WANDB_API_KEY` flag with `--env WANDB_MODE=offline`.

#### Alpaca
Launch the training job with the following line (will be launched on a single node with 4 A100-80GB GPUs)
```
sky launch -c alpaca -s scripts/train-alpaca.yaml --env WANDB_API_KEY
```

### Fine-tuning with Local GPUs
Vicuna can also be trained on 8 A100 GPUs with 80GB memory with the following code. To train on less GPUs, you can reduce the `per_device_train_batch_size` and increase the `gradient_accumulation_steps` accordingly to keep the global batch size the same. To setup the environment, please see the setup section in [scripts/train-vicuna.yaml](scripts/train-vicuna.yaml).
```bash
torchrun --nnodes=1 --nproc_per_node=8 --master_port=<your_random_port> \
    fastchat/train/train_flash_attn.py \
    --model_name_or_path <path-to-llama-model-weight> \
    --data_path <path-to-data> \
    --bf16 True \
    --output_dir ./checkpoints \
    --num_train_epochs 3 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 1200 \
    --save_total_limit 100 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --fsdp "full_shard auto_wrap" \
    --fsdp_transformer_layer_cls_to_wrap 'LlamaDecoderLayer' \
    --tf32 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --lazy_preprocess True
```

## Evaluation

