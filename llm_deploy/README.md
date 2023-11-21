## Deploy lora-finetuned model using vLLM variance

We need to use an unmerged branch to support deploying lora-finetuned model. (the forked repo is https://github.com/troph-team/vllm.git)

Go to the vllm dir and pip install -e .

To notice https://github.com/vllm-project/vllm/issues/1283, need to modify the config file to "== 2.0.1" and the pytorch version if facing with CUDA version error.


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
Submit gpu request and open a an interactive terminal
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
Implement the following python commands in three separate interactive terminal windows:
```bash
python3 -m fastchat.serve.controller
python3 -m fastchat.serve.model_worker --model-path model-checkpoint
python3 -m fastchat.serve.openai_api_server --host localhost --port 8000
```
Call model checkpoint API
```bash
curl http://localhost:8000/v1/completions \
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

## Access deployed Babel server on a local machine
Construct ssh tunnel between babel login node and babel compute node with hosted model
```bash
ssh -N -L 7662:localhost:8000 username@babel-x-xx
```
The above command creates a localhost:7662 server on bable login node which connects to localhost:8000 on compute node.

Construct ssh tunnel between local machine and babel login node
```bash
ssh -N -L 8001:localhost:7662 username@<mycluster>
```
The above command creates a localhost:8001 server on your local machine which connects to localhost:7662 on babel login node.

Call hosted model on local machine
```bash
curl http://localhost:8001/v1/models
```
If the above command runs successfully, you should be able to use REST API on your local machine.

(optional) If you fail in building the ssh tunnel, you may add `-v` to the ssh command to see what went wrong.




## Userful resource links for babel
1. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=BABEL#Cluster_Architecture
2. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=VSCode
3. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Training_Material
4. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Connecting_to_the_Cluster#Copying_Data_to_Compute_Nodes

# Deploy LLM on Babel (easy version)

We provide a detailed step by step instruction on how to deploy LLM on babel server.

#### Useful Commands

`squeue` to check the status of your current job ID

`scancel [ID]` to cancel your current job ID

`sinfo` to check all the compute nodes

#### How to deploy

1. `ssh <name>@babel.lti.cs.cmu.edu` to log in into the server to the login node

2. `conda activate [webarena]` to activate the current conda environment that your sbatch job wants to do

3. ```bash
   sbatch --gres=gpu:1 -t 72:00:00 -c4 --mem=80g --mail-type=ALL --mail-user=<andrew_id>@cs.cmu.edu -e <dir>/logs/out.err -o <dir>/logs/out.log <dir>/FastChat/run.sh
   ```

   run sbatch.sh in the FastChat directory

4. ```bash
   #!/bin/bash
   
   # Starting the controller
   python3 -m fastchat.serve.controller &
   
   # Starting the model worker with the specified model path
   python3 -m fastchat.serve.model_worker --model-path ./model-checkpoint &
   
   # Starting the OpenAI API server on host 0.0.0.0 and port 8000
   python3 -m fastchat.serve.openai_api_server --host 0.0.0.0 --port 8000
   ```

		In the FastChat directory. The host needs to be **0.0.0.0** instead of localhost.

5. After running that, on our local machine:

   ```bash
   ssh -L 8001:10.1.1.36:8000 <name>@babel.lti.cs.cmu.edu
   ```

   10.1.1.36 is the compute node for our machine (which could be got using `ifconfig` command on the compute node when `ssh babel-2-13` into that), 8000 is the port it exports and 8001 is the localhost port that we want to use. After running that, it would automatically jump to the babel-login node so that but we need to make it open when we are trying to call the model.

6. After having tested that, we could curl on them:

   ```bash
   curl http://localhost:8001/v1/models
   ```

   to check the status of the model.

   We could curl on requesting the model:

   ```
   curl http://localhost:8001/v1/completions \                 
        -H "Content-Type: application/json" \
        -d '{
            "model": "webarena-mistral-7b-ckpt",
            "prompt": "San Francisco is a",
            "max_tokens": 7,
            "temperature": 0
        }'
   ```



Therefore, the sbatch could remain for at most 3 days. And during the calling of our models, we need to keep the ssh -L running and call it using curl.
