#!/bin/bash
cd /home/ruiyiwan/sotopia

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/selftrain_scripts/config/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HFSDNWG78KV60B0H60GQNNF9", "01HFSDNWGPJSBBS6HT8GDWMC9Q", "01HFSDNWG5Z99ZX40DHZY88PY8", "01HFSDNWHDNSAWC41SWM1ZXTCG", "01HFSDNWGMHY3VNT4BGDXP0GZN", "01HFSDNWG1WFWWBEMMQ0M694BG"]' \
    '--gin.AGENT1_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-1_checkpoint-base_epoch_2_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=False' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-1_checkpoint-base_epoch_2_gpt-3.5-turbo_dev"'
done

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/selftrain_scripts/config/generate.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HFSDNWG78KV60B0H60GQNNF9", "01HFSDNWGPJSBBS6HT8GDWMC9Q", "01HFSDNWG5Z99ZX40DHZY88PY8", "01HFSDNWHDNSAWC41SWM1ZXTCG", "01HFSDNWGMHY3VNT4BGDXP0GZN", "01HFSDNWG1WFWWBEMMQ0M694BG"]' \
    '--gin.AGENT2_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="pilot-1_checkpoint-base_epoch_2_gpt-3.5-turbo_dev"' \
    '--gin.PUSH_TO_DB=False' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="pilot-1_checkpoint-base_epoch_2_gpt-3.5-turbo_dev"'
done

if [ $? -eq 0 ]; then
    echo "Success" > /home/ruiyiwan/selftrain_scripts/logs/pilot-1/eval_status_checkpoint-base_epoch_2.txt
else
    echo "Failed" > /home/ruiyiwan/selftrain_scripts/logs/pilot-1/eval_status_checkpoint-base_epoch_2.txt
fi
