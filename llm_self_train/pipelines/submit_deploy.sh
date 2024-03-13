#!/bin/bash

python3 /home/ruiyiwan/sotopia-llm/llm_self_train/pipelines/monitor_deploy_and_run_eval.py &

python3 /home/ruiyiwan/sotopia-llm/llm_self_train/pipelines/monitor_eval_and_stop_deploy.py --ckpt-name checkpoint_improve-0_epoch-19 &

# Starting the controller
python3 -m fastchat.serve.controller --port 23020 &

# Starting the model worker with the specified model path
python3 -m fastchat.serve.model_worker --model-path /data/tir/projects/tir6/bisk/ruiyiwan/selftrain/init-selftrain-round-2/checkpoint_improve-0_epoch-19 --worker-address http://localhost:21020 --controller-address http://localhost:23020 --port 21020 &

# Starting the OpenAI API server on host 0.0.0.0 and port 8000
python3 -m fastchat.serve.openai_api_server --host 0.0.0.0 --port 8020 --controller-address http://localhost:23020
