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
