#!/usr/bin/bash
# train_sotopia
#
#SBATCH --mem 80G
#SBATCH --gres gpu:4
#SBATCH -t 12:00:00
#SBATCH -o train_logs/selftrain-sft-round-1-filtered-top-2.out
#SBATCH -e train_logs/selftrain-sft-round-1-filtered-top-2.err
#SBATCH --exclude babel-7-37,shire-1-6,babel-3-32,babel-8-19,babel-4-7,babel-3-36,babel-8-7,babel-4-13,babel-4-28,babel-4-18,babel-3-3,babel-6-5,inst-0-35,babel-4-23,babel-8-11,babel-6-7,babel-6-9,babel-6-11,babel-6-13,babel-6-15,babel-0-37

bash train.sh
