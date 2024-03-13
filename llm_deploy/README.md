# LLM Deployment Pipeline
The following sections decribe how to deploy the fine-tuned LLMs on the [babel server](https://hpc.lti.cs.cmu.edu/wiki/index.php?title=BABEL) via [Fastchat](https://github.com/lm-sys/FastChat) and/or [vllm](https://github.com/vllm-project/vllm).

## Setting up Babel server

### Login with SSH key
Add public ed25519 key to server
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub <username>@<mycluster>
```
Config SSH file
```bash
 Host <mycluster>
 HostName <mycluster>
 User <username>
 IdentityFile ~/.ssh/id_ed25519
```
Login babel with SSH key
```bash
ssh <mycluster>
```

### Connecting to a compute node
Jump from login node to compute node
```bash
srun --pty bash
```
Check if you can access the /data/folder
```bash
cd /data/datasets/
```

### Config environment on the compute node
Install miniconda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda init
conda create --name myenv
conda activate myenv
# conda deactivate
```
Install vllm packages
```bash
conda install pip
pip install vllm
```
Install fastchat packages
```bash
conda install pip
git clone https://github.com/lm-sys/FastChat.git
cd FastChat
pip3 install --upgrade pip
pip3 install "fschat[model_worker,webui]"
```
Submit gpu request and open an interactive terminal
```bash
srun --gres=gpu:1 --time=1-00:00:00 --mem=80G --pty $SHELL
conda activate myenv
```
Some useful commands for checking gpu jobs
```bash
# check slurm status
squeue -l
# check gpu status
nvidia-smi
# check gpu usage
pip install gpustat
watch -n 1 gpustat
# quit slurm jobs
scancel job_id
# connect to compute node directly
ssh -J babel babel-x-xx
```

### Install cuda-toolkit (optional)
Due to the issue with vllm: https://github.com/vllm-project/vllm/issues/1283, we need to use cuda-toolkit=11.7.0 that is compatible with Pytorch 2.0.1.
Install cuda-toolkit=11.7.0 on conda environment
```bash
conda install -c "nvidia/label/cuda-11.7.0" cuda-toolkit
```
Check cuda-toolkit version
```bash
nvcc -V
```

## Deploy models on Babel via FastChat API server
Submit an sbatch job for `fastchat_deploy.sh` on the babel login node (See `deploy.sbatch` as an example). Use `squeue -u [user_name]` to see your compute nodes. Use `scancel [job_id]` if you want to cancel the job. L

Then we log onto the compute node for the job and check if the model is successfully deployed. Use `ssh -J babel babel-x-xx` to log onto the selected compute node. The following is an example of checking the deployment.
```bash
curl http://localhost:8003/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
         "model": "model-checkpoint",
         "prompt": "San Francisco is a",
         "max_tokens": 7,
         "temperature": 0
     }'
```
*Sample output:*
```JSON
{"id":"cmpl-GGvKBiZFdFLzPq2HdtuxbC","object":"text_completion","created":1698692212,"model":"checkpoint-4525","choices":[{"index":0,"text":"city that is known for its icon","logprobs":null,"finish_reason":"length"}],"usage":{"prompt_tokens":5,"total_tokens":11,"completion_tokens":6}}
```

### Deploy on your local machine
An SSH tunnel needs to be established in order to deploy the model on your local computer. We need to first record the inet IP address of the babel compute node.

On the compute node that you deployed your model, use command `ifconfig` and get the inet address (e.g. `10.0.0.168`). 

On your local computer, construct the SSH tunel. The following command creates such tunnel between port 8003 on babel and port 8004 on our local computer:
```bash
ssh -N -L 8003:10.0.0.168:8004 username@babel-x-xx
```

Then you are able to call your deployed model API on your local computer using command `curl http://localhost:8004/v1/models`


## Deploy models on Babel via vllm API server
Start vLLM surver with model checkpoint
```bash
python -m vllm.entrypoints.openai.api_server --model model_checkpoint/
```
Call model checkpoint API
```bash
curl http://localhost:8000/v1/models
```
*Sample output:*
```JSON
{"object":"list","data":[{"id":"Mistral-7B-Instruct-v0.1/","object":"model","created":1697599903,"owned_by":"vllm","root":"Mistral-7B-Instruct-v0.1/","parent":null,"permission":[{"id":"modelperm-d415ecf6362a4f818090eb6428e0cac9","object":"model_permission","created":1697599903,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}
```
Inference model checkpoint API
```bash
curl http://localhost:8000/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
         "model": "model_checkpoint",
         "prompt": "San Francisco is a",
         "max_tokens": 7,
         "temperature": 0
     }'
```
*Sample output:*
```JSON
{"id":"cmpl-bf7552957a8a4bd89186051c40c52de4","object":"text_completion","created":3600699,"model":"Mistral-7B-Instruct-v0.1/","choices":[{"index":0,"text":" city that is known for its icon","logprobs":null,"finish_reason":"length"}],"usage":{"prompt_tokens":5,"total_tokens":12,"completion_tokens":7}}
```

# Userful resources 
## Links for babel tutorials
1. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=BABEL#Cluster_Architecture
2. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=VSCode
3. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Training_Material
4. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Connecting_to_the_Cluster#Copying_Data_to_Compute_Nodes

## Deploy lora-finetuned model using vLLM variance

We need to use an unmerged branch to support deploying lora-finetuned model. (the forked repo is https://github.com/troph-team/vllm.git)

Go to the vllm dir and pip install -e .

To notice https://github.com/vllm-project/vllm/issues/1283, need to modify the config file to "== 2.0.1" and the pytorch version if facing with CUDA version error.
