# Data Generation

For the first step, we generate envProfile (including scenario / social goal / relationship restriction) based on inspiring prompt.

For the 2.1 step, we put the original agentProfile and relationshipProfile into our new redis database

For the 2.2 step, we combine them together to be combos based on conditiona sampling (the restriction is the relationship)

All the EnvProfile (new generated), AgentProfile (sotopia original), RelationshipProfile (sotopia original), and envagentcombo are on the redis database that is new created.

For the third step, we need to use another version of redis and convert it into json file and save the whole data in the database on the local machine.

For the final step, we convert the whole thing into Ruiyi's format.

# Local Redis Setting
Since the redis-server cannot directly input json data, it requires loading a RedisJson model into the redis-server to enable this function. Therefore, we need to load a docker based on RedisJson:

docker run -p 6379:6379 --name redis-stack redis/redis-stack:latest

Link: <https://github.com/RedisJSON/RedisJSON>


### Redis Version Issue

The default version for redis could be 7.2.x. However, to deploy it on tiger, we need to use the 6.2.x version of redis. Therefore, the command line running on local could be:

`docker run -p 6379:6379 --name redis-stack-old redis/redis-stack:6.2.6-v10` instead of using latest. After running on local and save all data to redis db, we should get a dump.rdb in the folder that are in version 6.2.6. We could then upload this file to tiger server. 

# Redis on Server - USE this all in one tuturial as the latest instruction for hosting redis db
We are using CMU Tiger to host our Redis Database. The current host port is 8008 and redis port is 6388.

### Connecting to Redis
To connect to Redis DB for loading and saving, follow the steps:
1. When activate conda environment, enter:
   
`conda env config vars set REDIS_OM_URL="redis://:PASSWORD@server_name:port_num"`

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
   
   `ssh USERNAME@server_name` >>> enter password
2. Create conda environment and activate:

   `conda create -n sotopia python=3.11; conda activate sotopia; conda install -c conda-forge pip`
3. Locate the initial dataset to start the server. The dataset should be a dump.rdb from your local or from available sources by `curl` or `wget`.
   To copy a local dump.rdb to TIGER, use

   `scp localpath/dir/dump.rdb USERNAME@server_name:/serverfolder/dump.rdb`

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

REDIS_OM_URL="redis://:password@server_name:port_num"

Step to connect to the correct REDIS database as below:

1. conda env config vars set REDIS_OM_URL="redis://:password@server_name:port_num"
2. In python, use os to setup REDIS_OM_URL
3. To view the database visually, go to http://server_name:8008/redis-stack/browser

To setup Redis on Tiger, an example docker command is as below:

docker run -d --name CONTAINERNAME -p PORT:6379 -p PORT:8001 -v /home/PATH/FOLDER/:/data/ -e REDIS_ARGS="--save 60 1000 --requirepass PASSWORD" redis/redis-stack:latest

