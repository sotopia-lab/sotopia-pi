#!/bin/bash
cd /home/ruiyiwan/sotopia

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/resources/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPMD5KHA2JT3DNJ9ZGVPBT8"]' \
    '--gin.AGENT1_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-1_checkpoint-base_epoch_1_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-1_checkpoint-base_epoch_1_gpt-3.5-turbo_dev"'
done

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/resources/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPMD5KHA2JT3DNJ9ZGVPBT8"]' \
    '--gin.AGENT2_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-1_checkpoint-base_epoch_1_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-1_checkpoint-base_epoch_1_gpt-3.5-turbo_dev"'
done

if [ $? -eq 0 ]; then
    echo "Success" > /home/ruiyiwan/sotopia-llm/llm_self_train/logs/pilot-1/eval_status_checkpoint-base_epoch_1.txt
else
    echo "Failed" > /home/ruiyiwan/sotopia-llm/llm_self_train/logs/pilot-1/eval_status_checkpoint-base_epoch_1.txt
fi
