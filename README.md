# FastChat
An open platform for training, serving, and evaluating large language model based chatbots.

## Release

<p align="center">
<a href="https://vicuna.lmsys.org"><img src="assets/vicuna-logo.jpeg" width="20%"></a>
</p>

- 🔥 We released **Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90% ChatGPT Quality**. Checkout the blog [post](https://vicuna.lmsys.org) and [demo](https://chat.lmsys.org/).

<a href="https://chat.lmsys.org"><img src="assets/demo-narrow.gif" width="70%"></a>

Join our [Discord](https://discord.gg/h6kCZb72G7) server and follow our [Twitter](https://twitter.com/lmsysorg) to get the latest updates.

## Contents
- [Install](#install)
- [Vicuna Weights](#vicuna-weights)
- [Inference with Command Line Interface](#inference-with-command-line-interface)
- [Serving with Web GUI](#serving-with-web-gui)
- [Evaluation](#evaluation)
- [Fine-tuning](#fine-tuning)

## Install

### Method 1: With pip

```bash
# Install FastChat
pip3 install fschat

# Install the latest main branch of huggingface/transformers
pip3 install git+https://github.com/huggingface/transformers
```

### Method 2: From source

1. Clone this repository and navigate to the FastChat folder
```bash
git clone https://github.com/lm-sys/FastChat.git
cd FastChat
```

If you are running on Mac:
```bash
brew install rust cmake
```

2. Install Package
```bash
pip3 install --upgrade pip  # enable PEP 660 support
pip3 install -e .
```

## Vicuna Weights
We release [Vicuna](https://vicuna.lmsys.org/) weights as delta weights to comply with the LLaMA model license.
You can add our delta to the original LLaMA weights to obtain the Vicuna weights. Instructions:

1. Get the original LLaMA weights in the huggingface format by following the instructions [here](https://huggingface.co/docs/transformers/main/model_doc/llama).
2. Use the following scripts to get Vicuna weights by applying our delta. They will automatically download delta weights from our Hugging Face [account](https://huggingface.co/lmsys).

**NOTE**:
Our released weights are only compatible with the latest main branch of huggingface/transformers.
We install the correct version of transformers when fastchat is installed.

### Vicuna-13B
This conversion command needs around 60 GB of CPU RAM.
If you do not have enough memory, you can create a large swap file that allows the operating system to automatically utilize the disk as virtual memory.
```bash
python3 -m fastchat.model.apply_delta \
    --base /path/to/llama-13b \
    --target /output/path/to/vicuna-13b \
    --delta lmsys/vicuna-13b-delta-v0
```

### Vicuna-7B
This conversion command needs around 30 GB of CPU RAM.
If you do not have enough memory, you can create a large swap file that allows the operating system to automatically utilize the disk as virtual memory.
```bash
python3 -m fastchat.model.apply_delta \
    --base /path/to/llama-7b \
    --target /output/path/to/vicuna-7b \
    --delta lmsys/vicuna-7b-delta-v0
```

## Inference with Command Line Interface

(Experimental Feature: You can specify `--style rich` to enable rich text output and better text streaming quality for some non-ASCII content. This may not work properly on certain terminals.)

#### Single GPU
The command below requires around 28GB of GPU memory for Vicuna-13B and 14GB of GPU memory for Vicuna-7B.
See the "No Enough Memory" section below if you do not have enough memory.
```
python3 -m fastchat.serve.cli --model-path /path/to/vicuna/weights
```

#### Multiple GPUs
If you do not have enough GPU memory, you can use model parallelism to aggregate memory from multiple GPUs on the same machine.
```
python3 -m fastchat.serve.cli --model-path /path/to/vicuna/weights --num-gpus 2
```

#### CPU Only
This runs on the CPU only and does not require GPU. It requires around 60GB of CPU memory for Vicuna-13B and around 30GB of CPU memory for Vicuna-7B.
```
python3 -m fastchat.serve.cli --model-path /path/to/vicuna/weights --device cpu
```

#### Metal Backend (Mac Computers with Apple Silicon or AMD GPUs)
Use `--device mps` to enable GPU acceleration on Mac computers (requires torch >= 2.0).
Use `--load-8bit` to turn on 8-bit compression.
```
python3 -m fastchat.serve.cli --model-path /path/to/vicuna/weights --device mps --load-8bit
```
Vicuna-7B can run on a 32GB M1 Macbook with 1 - 2 words / second.

#### No Enough Memory or Other Platforms
If you do not have enough memory, you can enable 8-bit compression by adding `--load-8bit` to commands above.
This can reduce memory usage by around half with slightly degraded model quality.
It is compatible with the CPU, GPU, and Metal backend.
Vicuna-13B with 8-bit compression can run on a single NVIDIA 3090/4080/V100(16GB) GPU.

```
python3 -m fastchat.serve.cli --model-path /path/to/vicuna/weights --load-8bit
```

Besides, we are actively exploring more methods to make the model easier to run on more platforms.
Contributions and pull requests are welcome.

## Serving with Web GUI

To serve using the web UI, you need three main components: web servers that interface with users, model workers that host one or more models, and a controller to coordinate the webserver and model workers. Here are the commands to follow in your terminal:

#### Launch the controller
```bash
python3 -m fastchat.serve.controller
```

This controller manages the distributed workers.

#### Launch the model worker
```bash
python3 -m fastchat.serve.model_worker --model-path /path/to/vicuna/weights
```
Wait until the process finishes loading the model and you see "Uvicorn running on ...". You can launch multiple model workers to serve multiple models concurrently. The model worker will connect to the controller automatically.

To ensure that your model worker is connected to your controller properly, send a test message using the following command:
```bash
python3 -m fastchat.serve.test_message --model-name vicuna-13b
```

#### Launch the Gradio web server
```bash
python3 -m fastchat.serve.gradio_web_server
```

This is the user interface that users will interact with.

By following these steps, you will be able to serve your models using the web UI. You can open your browser and chat with a model now.


## Evaluation

Our AI-enhanced evaluation pipeline is based on GPT-4. This section provides a high-level summary of the pipeline. For detailed instructions, please refer to the [evaluation](fastchat/eval) documentation.

### Pipeline Steps

1. Generate answers from different models: Use `qa_baseline_gpt35.py` for ChatGPT, or specify the model checkpoint and run `get_model_answer.py` for Vicuna and other models.

2. Generate reviews with GPT-4: Use GPT-4 to generate reviews automatically. This step can also be performed manually if the GPT-4 API is not available to you.

3. Generate visualization data: Run `generate_webpage_data_from_table.py` to generate data for a static website, which allows you to visualize the evaluation data.

4. Visualize the data: Serve a static website under the `webpage` directory. You can use `python3 -m http.server` to serve the website locally.

### Data Format and Contribution

We use a data format encoded with JSON Lines for evaluation. The format includes information on models, prompts, reviewers, questions, answers, and reviews.

You can customize the evaluation process or contribute to our project by accessing the relevant [data](fastchat/eval/table/).

For detailed instructions, please refer to the [evaluation](fastchat/eval) documentation.

## Fine-tuning
### Data

Vicuna is created by fine-tuning a LLaMA base model using approximately 70K user-shared conversations gathered from ShareGPT.com with public APIs. To ensure data quality, we convert the HTML back to markdown and filter out some inappropriate or low-quality samples. Additionally, we divide lengthy conversations into smaller segments that fit the model's maximum context length. For detailed instructions to clean the ShareGPT data, check out [here](docs/commands/data_cleaning.md).

Due to some concerns, we may not release the data at the moment. If you would like to try the fine-tuning code, you can try to run it with our [preprocessed alpaca dataset](playground/data/alpaca-data-conversation.json) (originally from [here](https://github.com/tatsu-lab/stanford_alpaca)).

### Code and Hyperparameters
We fine-tune the model using the code from [Stanford Alpaca](https://github.com/tatsu-lab/stanford_alpaca), with some modifications to support gradient checkpointing and [Flash Attention](https://github.com/HazyResearch/flash-attention). We use similar hyperparameters as the Stanford Alpaca.

| Hyperparameter | Global Batch Size | Learning rate | Epochs | Max length | Weight decay |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vicuna-13B | 128 | 2e-5 | 3 | 2048 | 0 |

### Fine-tuning on Any Cloud with SkyPilot
[SkyPilot](https://github.com/skypilot-org/skypilot) is a framework built by UC Berkeley for easily and cost effectively running ML workloads on any cloud (AWS, GCP, Azure, Lambda, etc.). 
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
# Launch it on managed spot to save 3x cost (train Vicuna-13B with around $300)
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
Vicuna can also be trained on 8 A100 GPUs with 80GB memory with the following code. To train on fewer GPUs, you can reduce the `per_device_train_batch_size` and increase the `gradient_accumulation_steps` accordingly to keep the global batch size the same. To setup the environment, please see the setup section in [scripts/train-vicuna.yaml](scripts/train-vicuna.yaml).
```bash
torchrun --nnodes=1 --nproc_per_node=8 --master_port=<your_random_port> \
    fastchat/train/train_mem.py \
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
