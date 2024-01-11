#!/bin/bash
cd /home/ruiyiwan/sotopia

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/resources/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPQ34Y3S1TDPTRX1CCH6VPG", "01HJPQ34ZG9WZEDX6BV5QZB1QG"]' \
    '--gin.AGENT1_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-3_checkpoint_improve-0_epoch-19_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-3_checkpoint_improve-0_epoch-19_gpt-3.5-turbo_dev"'
done

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/resources/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPQ34Y3S1TDPTRX1CCH6VPG", "01HJPQ34ZG9WZEDX6BV5QZB1QG"]' \
    '--gin.AGENT2_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-3_checkpoint_improve-0_epoch-19_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-3_checkpoint_improve-0_epoch-19_gpt-3.5-turbo_dev"'
done

if [ $? -eq 0 ]; then
    echo "Success" > /home/ruiyiwan/sotopia-llm/llm_self_train/logs/pilot-3/eval_status_checkpoint_improve-0_epoch-19.txt
else
    echo "Failed" > /home/ruiyiwan/sotopia-llm/llm_self_train/logs/pilot-3/eval_status_checkpoint_improve-0_epoch-19.txt
fi
