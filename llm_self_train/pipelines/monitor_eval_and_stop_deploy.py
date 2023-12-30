import yaml
import os
import argparse
import time

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

with open("resources/deploy_config.yml", 'r') as f:
    deploy_config = yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt-name', type=str, required=True)
    args = parser.parse_args()

    while True:
        if os.path.isfile(f"{deploy_config['log_dir']}/eval_status_{args.ckpt_name}.txt"):
            with open(os.path.join(deploy_config['tmp_dir'], "map_ckpt_job.txt"), 'r') as f:
                lines = f.readlines()
            for line in lines:
                ckpt, job_id = line.strip().split(":")
                if ckpt == args.ckpt_name:
                    new_lines = []
                    if os.path.isfile(os.path.join(deploy_config['tmp_dir'], "scancel_list.txt")):
                        with open(os.path.join(deploy_config['tmp_dir'], "scancel_list.txt"), 'r') as f:
                            new_lines = f.readlines()
                    new_lines.append(f"{job_id}\n")

                    with open(os.path.join(deploy_config['tmp_dir'], "scancel_list.txt"), 'w') as f:
                        f.writelines(new_lines)

                    break
                
            break
        time.sleep(30)


if __name__ == "__main__":
    main()