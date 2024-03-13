cd /Users/pamela/Documents/capstone/sotopia

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /Users/pamela/Documents/capstone/sotopia-llm/data_generate/scripts/sotopia_conf/generation_utils_conf/generate_mistral_gpt-3.5-turbo.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01H7VFHNV13MHN97GAH73E3KM8", "01H7VFHN5WVC5HKKVBHZBA553R", "01H7VFHN9W0WAFZCBT09PKJJNK", "01H7VFHPDZVVCDZR3AARA547CY", "01H7VFHPQQQY6H4DNC6NBQ8XTG", "01H7VFHN7WJK7VWVRZZTQ6DX9T", "01H7VFHPS5WJW2694R1MNC8JFY", "01H7VFHNN7XTR99319DS8KZCQM", "01H7VFHQ11NAMZS4A2RDGDB01V", "01H7VFHPSWGDGEYRP63H2DJKV0", "01H7VFHNF4G18PC9JHGRC8A1R6", "01H7VFHNNYH3W0VRWVY178K2TK", "01H7VFHP8AN5643B0NR0NP00VE", "01H7VFHN7A1ZX5KSMT2YN9RXC4"]' \
    '--gin.AGENT1_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="sft-selftrain-round-3-filtered-top-2_checkpoint_improve-0_epoch-5_gpt-3.5-turbo_test"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="sft-selftrain-round-3-filtered-top-2_checkpoint_improve-0_epoch-5_gpt-3.5-turbo_test"'
done

for i in {1..5}; do
    python -m examples.experiment_eval \
    --gin_file /Users/pamela/Documents/capstone/sotopia-llm/data_generate/scripts/sotopia_conf/generation_utils_conf/generate_mistral_gpt-3.5-turbo.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01H7VFHNV13MHN97GAH73E3KM8", "01H7VFHN5WVC5HKKVBHZBA553R", "01H7VFHN9W0WAFZCBT09PKJJNK", "01H7VFHPDZVVCDZR3AARA547CY", "01H7VFHPQQQY6H4DNC6NBQ8XTG", "01H7VFHN7WJK7VWVRZZTQ6DX9T", "01H7VFHPS5WJW2694R1MNC8JFY", "01H7VFHNN7XTR99319DS8KZCQM", "01H7VFHQ11NAMZS4A2RDGDB01V", "01H7VFHPSWGDGEYRP63H2DJKV0", "01H7VFHNF4G18PC9JHGRC8A1R6", "01H7VFHNNYH3W0VRWVY178K2TK", "01H7VFHP8AN5643B0NR0NP00VE", "01H7VFHN7A1ZX5KSMT2YN9RXC4"]' \
    '--gin.AGENT2_MODEL="gpt-3.5-turbo"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="sft-selftrain-round-3-filtered-top-2_checkpoint_improve-0_epoch-5_gpt-3.5-turbo_test"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="sft-selftrain-round-3-filtered-top-2_checkpoint_improve-0_epoch-5_gpt-3.5-turbo_test"'
done
