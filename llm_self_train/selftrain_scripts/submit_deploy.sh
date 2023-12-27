#!/bin/bash

python3 /home/ruiyiwan/selftrain_scripts/monitor_deploy_and_run_eval.py &

# Starting the controller
python3 -m fastchat.serve.controller &

# Starting the model worker with the specified model path
python3 -m fastchat.serve.model_worker --model-path /data/tir/projects/tir6/bisk/ruiyiwan/selftrain/pilot-1/checkpoint-base_epoch_2 &

# Starting the OpenAI API server on host 0.0.0.0 and port 8000
python3 -m fastchat.serve.openai_api_server --host 0.0.0.0 --port 8010