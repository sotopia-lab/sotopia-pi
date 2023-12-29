import yaml
import os
import json
import subprocess
import time
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

with open("resources/deploy_config.yml", 'r') as f:
    deploy_config = yaml.safe_load(f)


def try_parsing_json(json_string):
    try:
        return json.loads(json_string), True
    except json.JSONDecodeError:
        return None, False
    

def check_deployment_ready():
    count = 0
    while True:
        if count > deploy_config["deploy_check_max_round"]:
            return False
        
        # Curl the checkpoint API and save curl output
        if not os.path.exists(os.path.join(deploy_config["tmp_dir"], "curl_result.txt")):
            with open(os.path.join(deploy_config["tmp_dir"], "curl_result.txt"), 'w'):
                pass
        commands = f"""
            curl http://0.0.0.0:{deploy_config["deploy_port"]}/v1/models > {deploy_config["tmp_dir"]}/curl_result.txt
        """
        subprocess.run(commands, shell=True)
        with open(os.path.join(deploy_config["tmp_dir"], "curl_result.txt"), 'r') as f:
            line = f.readlines()
        if line:
            parsed_string, is_json = try_parsing_json(line[0])
            if is_json:
                # Model deploy is successful if the data component has elements
                if len(parsed_string["data"]) > 0:
                    return True
            else: # Model deployment is not successful is curl does not receive a json object
                break
        # If deployment is not ready yet
        count += 1
        time.sleep(20)

    return False


def run_eval():
    commands = f"""
    cd {config['script_dir']}
    conda activate myenv
    bash pipelines/submit_eval.sh > {deploy_config['log_dir']}/eval_results_{deploy_config['ckpt_name']}.txt
    """
    subprocess.run(commands, shell=True)
        

def main():
    if check_deployment_ready():
        with open(os.path.join(deploy_config["log_dir"], f"eval_monitor_success_{deploy_config['ckpt_name']}"), 'w') as f:
            f.write("")
        run_eval()
        
    else:
        with open(os.path.join(deploy_config["log_dir"], f"eval_monitor_fail_{deploy_config['ckpt_name']}"), 'w') as f:
            f.write("")
    
        
if __name__ == "__main__":
    main()