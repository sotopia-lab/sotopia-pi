import json

import redis
from rejson import Client, Path

redis_host = "server_name"
redis_port = "port_num"
redis_password = "password"


def get_redisjson_value(r, key):
    try:
        return r.jsonget(key, Path.rootPath())
    except Exception as e:
        print(f"Could not retrieve JSON for key {key}: {e}")
        return None


if __name__ == "__main__":
    env_data = {}
    try:
        r = Client(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )
        keys = r.keys("*")

        for key in keys:
            if "EnvironmentProfile" in key:
                value = get_redisjson_value(r, key)
                env_data[key] = value

    except redis.ConnectionError:
        print("Failed to connect to Redis server.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print(len(env_data))

    for data in env_data.values():
        if (
            data["scenario"]
            == "A conversation between two individuals at a charity gala"
        ):
            import pdb

            pdb.set_trace()

    with open("./all_environment_profile.json", "w") as f:
        json.dump(env_data, f)
