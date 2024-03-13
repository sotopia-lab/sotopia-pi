#!/bin/bash

# Starting the controller
python3 -m fastchat.serve.controller &

# Starting the model worker with the specified model path
python3 -m fastchat.serve.model_worker --model-path /data/tir/projects/tir6/bisk/ruiyiwan/selftrain/pilot-2/checkpoint-4525 &

# Starting the OpenAI API server on host 0.0.0.0 and port 8000
python3 -m fastchat.serve.openai_api_server --host 0.0.0.0 --port 8003
