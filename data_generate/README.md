# Run Code
## Scenario Generation
[TODO]

## Conversation Data Generation
The first step is to sample scenarios for conversation generation. Running 
```python
python3 sample_scenarios.py --env-file env_files/used_env.json --num 100 --experiment-name SFT-round-1 --show-stat True
```
will save 100 sampled scenarios to `env_files/used_env.json` with experiment name "SFT-round-1". The `--show-stat` option provides a breakdown of the scenario distribution.

The second step is to generate conversation based on the SOTOPIA framework. Running
```python
python3 generate_conversations.py --eval-script scripts/generate_conv_sft.sh --env-file env_files/used_env.json --experiment-name SFT-round-1 --tag sft_round_1_gpt-4_gpt-4_clean --batch-size 4 --agent1-model gpt-4 --agent2-model gpt-4 --push-to-db True
```
will modify the bash file according to the provided parameters and start sotopia evaluation. If `push-to-db` is set to be `True`, then the episode logs will be pushed to the redis database.
(For more information about the args, run `python3 generate_conversations.py -h`)

# Scenario Generation
To generate scenarios, we first need to clean up the inspirational prompts using three datasets. Details of dataset selection are listed in data_generate folder, but to run the cleaning and merging codes for an inspirational prompt csv, run
```python
python3 create_inspirational_prompts.py
```
Next, we need to generate a preliminary pool of scenarios, say 430. To run the code for generation and auto-save to redis DB, run
```python
python3 generate_new_envs.py --num 430
```
Note that we use default GPT4-Turbo and Temperature 0.5 for generation. If you want to generate using different parameters and model, you should instead run
```python
python3 generate_new_envs.py --num 430 --gen_model "openAI model_name" --temperature 0.x
```


### Explanation for inspirational prompt:

For Sotopia's inspirational prompt, it includes cherry-pick a few examples from 6 datasets (`social\_iqa`, `social\_chem`, `normbank`, `deal-or-no-deal`, `persuation_for_good`, `mindcraft`)

For our inspirational prompt, it include full examples from 3 datasets (`social\_iqa`, `social\_chem`, `normbank`). 

Notice1: The reason why we does not include `deal-or-no-deal` and `mindcraft` is because we think those inspirational prompt is too similar within one dataset and would cause some leakage if we train on them and test on sotopia ones

Notice2: The reason why we do not include `persuation_for_good` is because we cannnot find the exact form of inspirational prompt that is the same with sotopia's inspirational prompt and the previous mentioed three datasets already provide enough inspirational prompts.



### Explanation for EnvProfile generation:

With inspirational prompt, we utilize `gpt-4-turbo` to generate EnvProfile. 

Note that our function also allow other OpenAI models with different temperature. The default model is gpt-4-turbo and default temperature is 0.5. 


### Detail Steps

1. We create new inspirational prompts csv under env_files folder, based on three sources used in SOTOPIA scenario generation. The sources are social_iqa, social_chemistry and normbank. For each source, we make sure the duplicates are dropped and there is NOT overlapping with SOTOPIA.
2. We generate 430 new scenarios, roughly evenly distributed across three sources. The logic to generate new scenarios is as follow:
<br> a. For a target amount of scenarios, we divide the number by three to get X(or number of total sources)
<br> b. For each source, we randomly select X number of unused prompts, and for each prompt, we randomly select an environment profile example currently in the database, then we use openAI completion with model and temperature to generate new scenario. 
<br> c. After generation, we save all used propmts, the corresponding pk and generate model in to used_prompts.csv under env_files, so as to track used prompts and avoid future repetition.

3. We also create sampling function that allow random sample from current redis database, and filter out SOTOPIA scenarios and used scenarios, which are saved under used_env.json. The reason is that we want to avoid generating conversation using the same scenarios, to keep diversity. 
   

### Detail Steps (deprecated)

For the zero step, we need to prepare new inspirational prompts as motivations of gpt-4-turbo to generate creative scenario and social goals.

For the first step, we generate envProfile (including scenario / social goal / relationship restriction) based on inspiring prompt.

For the 2.1 step, we put the original agentProfile and relationshipProfile into our new redis database

For the 2.2 step, we combine them together to be combos based on conditiona sampling (the restriction is the relationship)

All the EnvProfile (new generated), AgentProfile (sotopia original), RelationshipProfile (sotopia original), and envagentcombo are on the redis database that is new created.

For the third step, we need to use another version of redis and convert it into json file and save the whole data in the database on the local machine.

For the final step, we convert the whole thing into Ruiyi's format.


# Redis on Server - USE this all in one tuturial as the latest instruction for hosting redis db

We are using CMU Tiger to host our Redis Database. The current host port is 8008 and redis port is 6388.

### Connecting to Redis

To connect to Redis DB for loading and saving, follow the steps:

1. When activate conda environment, enter:

`conda env config vars set REDIS_OM_URL="redis://:PASSWORD@tiger.lti.cs.cmu.edu:6388"`

The password is only available to the development team, or upon request.

2. After setting REDIS_OM_URL in conda, you should reactivate your conda.

3. To load data from Redis, an example way is:

   `from sotopia.database.logs import EpisodeLog`

   `episode = EpisodeLog.get(pk = 'xxxxx')`

4. To save data from Redis, an example way is

   `Migrator().run()`

   `episode = EpisodeLog(**jsonfile)`

   `episode.save()`

### Hosting Redis on Server (TIGER)

To do so, one of the member must first have access to TIGER. Then, follow the steps:

1. Login:

   `ssh USERNAME@tiger.lti.cs.cmu.edu` >>> enter password

2. Create conda environment and activate:

   `conda create -n sotopia python=3.11; conda activate sotopia; conda install -c conda-forge pip`

3. Locate the initial dataset to start the server. The dataset should be a dump.rdb from your local or from available sources by `curl` or `wget`.
   To copy a local dump.rdb to TIGER, use

   `scp localpath/dir/dump.rdb USERNAME@tiger.lti.cs.cmu.edu:/serverfolder/dump.rdb`

   If serverfolder does not exist, you should first create a folder separately for the rdb file in TIGER.

4. Use docker run to start a Redis server:

   `docker run -d --name NAMEYOUWANT -p PORT1:6379 -p PORT2:8001 -v /home/USERNAME/serverfolder/:/data/ -e REDIS_ARGS="--save 60 1000 --requirepass PASSWORD" redis/redis-stack:7.2.0-v6`

* NAMEYOUWANT - name the docker container, such as my-redis-server

* PORT1 - change to any port that is not occupied

* PORT2 - this is the port you could use to access the database online, change to any port that is not occupied

* save 60 1000 - this specifies the Redis server to dump the dataset to disk every 60 seconds if at least 1000 keys changed

* PASSWORD - this restrict the access to redis DB

* 7.2.0-v6 - this is due to version incompatibility. On TIGER, redis version is current at 5.0.7, but the dump.rdb we are using is in version 7.2.3. Using latest redis-stack without specifying verison would lead to incompatibility. We must specified we want the redis-stack to run using a newer version of image. If the dump.rdb are in version 6.2.12 for example, `redis/redis-stack:latest` is enough.

To check the version of redis, run `redis-cli INFO SERVER` on command line. 

To check if the server is successfully running, you could either go online using `http://SERVER:PORT/redis-stack/browser`, or run `docker ps` on command line and see if the container named NAMEYOUWANT is running. 

=======

### Redis Version Issue

The default version for redis could be 7.2.x. However, to deploy it on tiger, we need to use the 6.2.x version of redis. Therefore, the command line could be:

`docker run -p 6379:6379 --name redis-stack-old redis/redis-stack:6.2.6-v10` instead of using latest.

### Redis URL

So we have setup the redis for hosting our own database, with the following URL:

REDIS_OM_URL="redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"

Step to connect to the correct REDIS database as below:

1. conda env config vars set REDIS_OM_URL="redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"
2. In python, use os to setup REDIS_OM_URL
3. To view the database visually, go to http://tiger.lti.cs.cmu.edu:8008/redis-stack/browser

To setup Redis on Tiger, an example docker command is as below:

docker run -d --name CONTAINERNAME -p PORT:6379 -p PORT:8001 -v /home/PATH/FOLDER/:/data/ -e REDIS_ARGS="--save 60 1000 --requirepass PASSWORD" redis/redis-stack:latest



# Local Redis Setting (deprecated)

Since the redis-server cannot directly input json data, it requires loading a RedisJson model into the redis-server to enable this function. Therefore, we need to load a docker based on RedisJson:

docker run -p 6379:6379 --name redis-stack redis/redis-stack:latest

Link: <https://github.com/RedisJSON/RedisJSON>


### Redis Version Issue

The default version for redis could be 7.2.x. However, to deploy it on tiger, we need to use the 6.2.x version of redis. Therefore, the command line running on local could be:

`docker run -p 6379:6379 --name redis-stack-old redis/redis-stack:6.2.6-v10` instead of using latest. After running on local and save all data to redis db, we should get a dump.rdb in the folder that are in version 6.2.6. We could then upload this file to tiger server. 
