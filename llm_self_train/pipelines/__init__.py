import os

import yaml

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

os.environ["REDIS_OM_URL"] = config["redis_om_url"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["service_account_key_location"]

with open("resources/deploy_config.yml", "r") as f:
    deploy_config = yaml.safe_load(f)

deploy_config["log_dir"] = f"{config['script_dir']}/logs/{config['experiment_name']}"
deploy_config["tmp_dir"] = f"{config['script_dir']}/tmp/{config['experiment_name']}"

with open("resources/deploy_config.yml", "w") as f:
    yaml.dump(deploy_config, f)
