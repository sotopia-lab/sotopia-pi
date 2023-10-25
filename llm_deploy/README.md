## Deploy lora-finetuned model using vLLM variance

We need to use an unmerged branch to support deploying lora-finetuned model. (the forked repo is https://github.com/troph-team/vllm.git)

Go to the vllm dir and pip install -e .

To notice https://github.com/vllm-project/vllm/issues/1283, need to modify the config file to "== 2.0.1" and the pytorch version if facing with CUDA version error.



## Deploy finetuned model on babel via vLLM
### Login with SSH key
1. Add public ed25519 key to server
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub <username>@<mycluster>
```
2. Config ~~/.ssh/config
```bash
 Host <mycluster>
 HostName <mycluster>
 User <username>
 IdentityFile ~/.ssh/id_ed25519
```
3. Login babel with SSH key
```bash
ssh <mycluster>
```

### Connecting to compute node
1. Jump from login node to compute node
```bash
srun --pty bash
```
2. Check if you can access the /data/folder
```bash
cd /data/datasets/
```

### Config environment on compute node
1. Install miniconda
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda init
conda create --name myenv
conda activate myenv
# conda deactivate
```
2. Install vllm packages
```bash
conda install pip
pip install vllm
```
3. Submit gpu request and open a new terminal
```bash
srun --gres=gpu:1 --time=1-00:00:00 --mem=80G --pty $SHELL
conda activate myenv
```
4. Useful commands for checking gpu jobs
```bash
# check slurm status
squeue -l
# check gpu status
nvidia-smi
# quit slurm jobs
scancel job_id
# connect to compute node directly
ssh -J babel babel-x-xx
```

### Host vLLM instance and run inference on server
1. Start vLLM surver with model checkpoint
```bash
python -m vllm.entrypoints.openai.api_server --model model_checkpoint/
```
1. Call model checkpoint API
```bash
curl http://localhost:8000/v1/models
```
*Sample output:*
```JSON
{"object":"list","data":[{"id":"Mistral-7B-Instruct-v0.1/","object":"model","created":1697599903,"owned_by":"vllm","root":"Mistral-7B-Instruct-v0.1/","parent":null,"permission":[{"id":"modelperm-d415ecf6362a4f818090eb6428e0cac9","object":"model_permission","created":1697599903,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}
```
2. Inference model checkpoint API
```bash
curl http://localhost:8000/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
         "model": "model_checkpoint/",
         "prompt": "San Francisco is a",
         "max_tokens": 7,
         "temperature": 0
     }'
```
*Sample output:*
```JSON
{"id":"cmpl-bf7552957a8a4bd89186051c40c52de4","object":"text_completion","created":3600699,"model":"Mistral-7B-Instruct-v0.1/","choices":[{"index":0,"text":" city that is known for its icon","logprobs":null,"finish_reason":"length"}],"usage":{"prompt_tokens":5,"total_tokens":12,"completion_tokens":7}}
```

### Access deployed babel server on a local machine
TODO


### Userful resource links for babel
1. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=BABEL#Cluster_Architecture
2. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=VSCode
3. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Training_Material
4. https://hpc.lti.cs.cmu.edu/wiki/index.php?title=Connecting_to_the_Cluster#Copying_Data_to_Compute_Nodes

