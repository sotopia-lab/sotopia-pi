#!/bin/bash
cd /home/ruiyiwan/sotopia

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/logs/init-selftrain-round-1-improve-1-2nd-exp/generate_checkpoint_improve-0_epoch-14.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01H7VFHNV13MHN97GAH73E3KM8", "01H7VFHN5WVC5HKKVBHZBA553R", "01H7VFHN9W0WAFZCBT09PKJJNK", "01H7VFHPDZVVCDZR3AARA547CY", "01H7VFHPQQQY6H4DNC6NBQ8XTG", "01H7VFHN7WJK7VWVRZZTQ6DX9T", "01H7VFHPS5WJW2694R1MNC8JFY", "01H7VFHNN7XTR99319DS8KZCQM", "01H7VFHQ11NAMZS4A2RDGDB01V", "01H7VFHPSWGDGEYRP63H2DJKV0", "01H7VFHNF4G18PC9JHGRC8A1R6", "01H7VFHNNYH3W0VRWVY178K2TK", "01H7VFHP8AN5643B0NR0NP00VE", "01H7VFHN7A1ZX5KSMT2YN9RXC4"]' \
    '--gin.AGENT1_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=2' \
    '--gin.TAG="init-selftrain-round-1-improve-1-2nd-exp_checkpoint_improve-0_epoch-14_gpt-3.5-turbo_test"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="init-selftrain-round-1-improve-1-2nd-exp_checkpoint_improve-0_epoch-14_gpt-3.5-turbo_test"'
done

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /home/ruiyiwan/sotopia-llm/llm_self_train/logs/init-selftrain-round-1-improve-1-2nd-exp/generate_checkpoint_improve-0_epoch-14.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01H7VFHNV13MHN97GAH73E3KM8", "01H7VFHN5WVC5HKKVBHZBA553R", "01H7VFHN9W0WAFZCBT09PKJJNK", "01H7VFHPDZVVCDZR3AARA547CY", "01H7VFHPQQQY6H4DNC6NBQ8XTG", "01H7VFHN7WJK7VWVRZZTQ6DX9T", "01H7VFHPS5WJW2694R1MNC8JFY", "01H7VFHNN7XTR99319DS8KZCQM", "01H7VFHQ11NAMZS4A2RDGDB01V", "01H7VFHPSWGDGEYRP63H2DJKV0", "01H7VFHNF4G18PC9JHGRC8A1R6", "01H7VFHNNYH3W0VRWVY178K2TK", "01H7VFHP8AN5643B0NR0NP00VE", "01H7VFHN7A1ZX5KSMT2YN9RXC4"]' \
    '--gin.AGENT2_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=2' \
    '--gin.TAG="init-selftrain-round-1-improve-1-2nd-exp_checkpoint_improve-0_epoch-14_gpt-3.5-turbo_test"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="init-selftrain-round-1-improve-1-2nd-exp_checkpoint_improve-0_epoch-14_gpt-3.5-turbo_test"'
done

if [ $? -eq 0 ]; then
    echo "Success" > /home/ruiyiwan/sotopia-llm/llm_self_train/logs/init-selftrain-round-1-improve-1-2nd-exp/eval_status_checkpoint_improve-0_epoch-14.txt
else
    echo "Failed" > /home/ruiyiwan/sotopia-llm/llm_self_train/logs/init-selftrain-round-1-improve-1-2nd-exp/eval_status_checkpoint_improve-0_epoch-14.txt
fi