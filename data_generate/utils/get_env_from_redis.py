from rejson import Client, Path
import json
import redis

redis_host = 'tiger.lti.cs.cmu.edu'
redis_port = 6388
redis_password = 'aclkasjf29qwrUOIO'

def get_redisjson_value(r, key):
    try:
        return r.jsonget(key, Path.rootPath())
    except Exception as e:
        print(f"Could not retrieve JSON for key {key}: {e}")
        return None

env_data = {}

try:
    r = Client(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
    keys = r.keys('*')

    for key in keys:
        if 'EnvironmentProfile' in key:
            value = get_redisjson_value(r, key)
            env_data[key] = value

except redis.ConnectionError:
    print("Failed to connect to Redis server.")
except Exception as e:
    print(f"An error occurred: {e}")

print(len(env_data))

with open('./all_environment_profile.json', 'w') as f:
    json.dump(env_data, f)
