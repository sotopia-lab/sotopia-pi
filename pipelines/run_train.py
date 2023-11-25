import yaml
import subprocess

with open('train_args.yaml', 'r') as file:
    config = yaml.safe_load(file)

def run():
    args = ["deepspeed", f"--num_gpus={config.num_gpus}" "src/train_bash.py"]
    for key, value in config.items():
        if key in config:
            value = getattr(config, key)
            
        if isinstance(value, bool):
            if value:
                args.append(f"--{key}")
        else:
            args.append(f"--{key}")
            args.append(str(value))

    subprocess.run(args)