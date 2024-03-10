#!/bin/bash
cd /home/ruiyiwan/sotopia

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/resources/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPQ34Y3S1TDPTRX1CCH6VPG"]' \
    '--gin.AGENT1_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-2_checkpoint_improve-0_epoch-2_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=False' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-2_checkpoint_improve-0_epoch-2_gpt-3.5-turbo_dev"'
done

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/resources/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPQ34Y3S1TDPTRX1CCH6VPG"]' \
    '--gin.AGENT2_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-2_checkpoint_improve-0_epoch-2_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=False' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-2_checkpoint_improve-0_epoch-2_gpt-3.5-turbo_dev"'
done