#!/usr/bin/bash
# deploy_sotopia
#
#SBATCH --mem 80G
#SBATCH --gres gpu:1
#SBATCH -t 12:00:00
#SBATCH -o deploy.out
#SBATCH -e deploy.err

bash fastchat_deploy.sh
