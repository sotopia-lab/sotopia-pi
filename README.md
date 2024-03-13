
# Sotopia-π: Interactive Learning of Socially Intelligent Language Agents
This is the official repo of the paper: [add arxiv link].
For highlights of the paper, please see our [website](https://sotopia-dev.vercel.app/projects/sotopia-pi).

![title](imgs/acl2024_teaser.png)

We introduce Sotopia-π, a method that improves the social intelligence of large language models (LLMs) through social interaction. The method involves three steps: (1) automatically generates new social tasks, (2) collects data from both expert policy and agent policy for training, and (3) updates agent policy based on positive data rated by GPT-4. The training and evaluation environment is based on the [Sotopia](https://github.com/XuhuiZhou/sotopia) framework.

## Preparations
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Set up OpenAI API key in conda environment
  ```bash
  conda env config vars set OPENAI_API_KEY=api_key
  ```
- A Redis database needs to be set up prior to running this repo. For detailed instructions of setting up Redis database, please refer to [this tutorial]([https://github.com/sotopia-lab/sotopia-pi/tree/main/data_generate](https://github.com/sotopia-lab/sotopia-pi/tree/main/data_generate#setting-up-redis-database)). Make sure to set up Redis OM url in conda environment
  ```bash
  conda env config vars set REDIS_OM_URL="redis://user:password@host:port"
  ```
## Step 1: Social Task Generation
The first step is to generate synthesized social tasks by sampling keywords from datasets and prompting GPT-4 Turbo to generate corresponding social tasks. For detailed implementation, please refer to [this section](https://github.com/sotopia-lab/sotopia-pi/tree/main/data_generate#social-task-generation).

## Step 2: Training Data Collection
The second step is to collect data from expert (GPT-4 vs. GPT-4) as behavior cloning trajectories and from self (our model vs. our model) as self-reinforcement trajectories.
To collect behavior cloning data, run
```bash
cd data_generate
python3 generate_conversations.py --eval-script scripts/eval_sft.sh --env-file env_files/used_env.json --experiment-name your_exp_name --tag your_tag --agent1-model gpt-4 --agent2-model gpt-4 --push-to-db True
```
To collect self-reinforcement data, run
```bash
cd data_generate
python3 generate_conversations.py --eval-script scripts/eval_sft.sh --env-file env_files/used_env.json --experiment-name your_exp_name --tag your_tag --agent1-model custom_model --agent2-model custom_model --push-to-db True
```
For detailed implementation, please refer to [this section](https://github.com/sotopia-lab/sotopia-pi/tree/main/data_generate#conversation-data-generation-for-training)

## Step 3: Agent Policy Update
This step requires (1) filter the collected conversation data based on GPT-4 ratings and (2) update the LLM's policy through fine-tuning.
- We filter data following [this pipeline](https://github.com/sotopia-lab/sotopia-pi/tree/main/data_process#data-processing-pipeline) and reformat data into training format.
- We fine-tune the model based on [Llama Factory](https://github.com/hiyouga/LLaMA-Factory). Please follow [this section](https://github.com/sotopia-lab/sotopia-pi/tree/main/llm_self_train#training-bc-andor-sr-pipeline) to implement QLoRA fine-tuning.

## Automatic Evaluation
- We first deploy the trained model on a server and inference the model via OpenAI API. See [this section](https://github.com/sotopia-lab/sotopia-pi/tree/main/llm_deploy#llm-deployment-pipeline) for detailed instructions of deploying a model via [FastChat](https://github.com/lm-sys/FastChat/tree/main) and [vllm](https://github.com/vllm-project/vllm).
- Then we evaluate our model based on the Sotopia framework. Please refer to [this section](https://github.com/sotopia-lab/sotopia-pi/tree/main/llm_deploy#llm-deployment-pipeline) and the [Sotopia](https://github.com/XuhuiZhou/sotopia) repo for more details.

## Human Evaluation

* We develop a personalized project based on oTree and release the human evaluation project via Prolific.
* Detailed instruction on reproducing human evaluation is mentioned [here](https://github.com/sotopia-lab/sotopia-pi/tree/main/human_eval).

## Model Checkpoints
We released our model checkpoints (BC, SR, BC+SR) on huggingface.
- [BC model](https://huggingface.co/cmu-lti/sotopia-pi-mistral-7b-BC)
- [SR model](https://huggingface.co/cmu-lti/sotopia-pi-mistral-7b-SR)
- [BC+SR model](https://huggingface.co/cmu-lti/sotopia-pi-mistral-7b-BC_SR)
