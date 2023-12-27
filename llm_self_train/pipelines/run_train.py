from pipelines import config

import yaml
import subprocess

with open('./resources/train_args.yml', 'r') as file:
    train_args = yaml.safe_load(file)

def run_sft(output_dir, improve_step, ):
    args = ["deepspeed", f"--num_gpus={config['num_gpus']}", "../llm_rl/src/train_bash.py"]
    for key, value in train_args.items():
        if key in config:
            value = config[key]
        if key == 'output_dir':
            value = output_dir
            
        if isinstance(value, bool):
            if value:
                args.append(f"--{key}")
        else:
            args.append(f"--{key}")
            args.append(str(value))
    args.append(f"--improve_step={improve_step}")

    subprocess.run(args)