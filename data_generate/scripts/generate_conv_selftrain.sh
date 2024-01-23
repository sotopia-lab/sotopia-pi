cd /Users/pamela/Documents/capstone/sotopia

for i in {1..3}; do
    python -m examples.experiment_eval \
    --gin_file /Users/pamela/Documents/capstone/sotopia-llm/data_generate/scripts/sotopia_conf/generation_utils_conf/generate_mistral_mistral.gin \
    --gin_file sotopia_conf/server_conf/server.gin \
    --gin_file sotopia_conf/run_async_server_in_batch.gin \
    '--gin.ENV_IDS=["01HJPMD5KZF6C4XRS39KMXWK39", "01HJPMD5MPYGA2WHH82K2Z13S8", "01HJPMD5NCGGKXQKBETH76PPG0", "01HJPQ335HRCMK86RZXX3245A3", "01HJPQ3367R2437H6HPX2MJD76", "01HJPQ336X745MQY1FH72DGSR4", "01HJPQ337KACYQKFSZEKS9F3SS", "01HJPQ338A10FM1ZYE51ESZHX1", "01HJPQ339JM832EQGBGG3QGX48", "01HJPQ33A91AZT5CSX4PFNRPKW", "01HJPQ33D705RRB75Z0TDPQ3YS", "01HJPQ33EP6E678RH26Q0ZDS4Q", "01HJPQ33FFAF1A8917QYFGG8S2", "01HJPQ33G6W0ZMAG5EKMJZJP2B", "01HJPQ33GWVVQWKSEC79C1JN8S", "01HJPQ33HNVVWB4S7WRCEPAWY4", "01HJPQ33K56XWEQ4YVRX5MBC2Q", "01HJPQ33MHGVCYRANR78DHASW5", "01HJPQ33N8G6WZVVK34ZZG8A8N", "01HJPQ33NYXCK63E6FF47F2Q3V", "01HJPQ33PM9T2CZZ5Q5KWEQ07Y", "01HJPQ33T971CF9VBZZ7NHSWHD", "01HJPQ33V00W6SBBRFHJVY06X5", "01HJPTHKY9BWB1S1MDM0B8E83D", "01HJPTHKZNK6BM2RJHRNY1H3GD", "01HJPTHM0WARWWMV0HBAC6XCQY", "01HJPTHM1JADWN8F8HJX88VTNX", "01HJPTHM30P0DT7W5MA1H0ZJQV", "01HJPTHM4CBFXEDJNZBJJXZ6Z9", "01HJPTHM53EDTGCAR81KRXW41M", "01HJPTHM5SMCM4DFRJJGCB6DCW", "01HJPTHM768MJHAEAW1SAET4F7", "01HJPTHM7XZR9STHF44Y7M4VQG", "01HJPMD5REZ4XC3RM2GXQWWXD7", "01HJPMD5S5A2M9QDA5044PH435", "01HJPMD5SWAM82KEZJQXG77TZ6", "01HJPQ34MNXXMVTAHX174647YA", "01HJPQ34NZYMHJ00EMBD6R3NJV", "01HJPQ34PNXSMR7GNE7A9C1VC6", "01HJPQ34R24ZGW7R7ERK4K0VWA", "01HJPQ34RMDPWK6KQ077WK9JC0", "01HJPQ34S6QRVZPVYYGK5QKZ4V", "01HJPQ34SWZEWXGGFDRDEA5EMS", "01HJPQ34VDHWPE4G9T88Q9CXP6", "01HJPQ34W41585EP7MQ3C9WAHH", "01HJPQ34WVTGBB7CK6CNG0QCY8", "01HJPQ34XDAYX632YKKD2J6XF1", "01HJPQ34Y3S1TDPTRX1CCH6VPG", "01HJPQ34ZG9WZEDX6BV5QZB1QG", "01HJPQ35060GM48AFNSCJMECZA", "01HJPQ350XMQFGD1XR1JP07HGE", "01HJPQ351KEXW7QH2KM4QNZGQK", "01HJPQ352AZ5BVHDB5XN09T1DN", "01HJPQ3531Q5GCT4QG44GY5W2S", "01HJPQ353SVM28W987V3978E0A", "01HJPQ356HXQ4X0JCWTMYRBYKX", "01HJPQ357TFY29XE1VFWF1M45X", "01HJPQ358FJXRS50GTYCZEPP4Y", "01HJPQ358XBETCTVFD54HARQKW", "01HJPQ359KFCYGGKPH0ZH8YBT1", "01HJPQ35AARQABTSVC8KRPMP2J", "01HJPTHNRV97A2K9H7PZWXP9ZC", "01HJPTHNSJXX5P1N665C4JJBF7", "01HJPTHNT8NP9WN059MBJW2P8Y", "01HJPTHNTZ34M11TFBWTG90HRZ", "01HJPTHNWHC06BQKDJEYBG2J5V", "01HJPTHP0DTAVEZPWWFFA5JCTS", "01HJPMD5P22RRE0M3EH5SJKBAQ", "01HJPMD5PSHNB5P0R7RBAM8FDM", "01HJPMD5QB241H5E90RDBJ3HEM", "01HJPMD5QR8AFTP4S3AJGW69NZ", "01HJPQ33W4CDZ35BD8K4K0JQ18", "01HJPQ33Z3M5F2PR1XA2TDBMTP", "01HJPQ340FZ5K93PDGTQPC0X2X", "01HJPQ342HHEB7237NNQ1SCX65", "01HJPQ3438TZ04NXH39TK7G2XM", "01HJPQ343YYJXYPYFKWM7S587Q", "01HJPQ347QXCMW4JMZNBXYRWTW", "01HJPQ348EB61X00D59WG6CR9E", "01HJPQ349772CCRAFJWYXYDFP3", "01HJPQ349S7J1YT9S0ZV84SMRF", "01HJPQ34AGD5SCZP2QJGN8E8MQ", "01HJPQ34B9X7MAY2GRDQBKSFXJ", "01HJPQ34C2EME19P31F4462QVA", "01HJPQ34DZ0JVBKF9G9EFC4RGC", "01HJPQ34EN6HRXAE0GVCVZJHMC", "01HJPQ34FBFQY3TF19RBSQN2QZ", "01HJPQ34G1EN08TF0Q44Q5W4K2", "01HJPQ34GR3FB0EVQ02FHS8HSK", "01HJPQ34J5PXTW9MQTNA02TSFV", "01HJPQ34JVRPARF2NM2N3WBGHW", "01HJPQ34KJYFHGXWB076ST7F8G", "01HJPTHMS6PKNZRESP0N9FWMEA", "01HJPTHMTKJ06SZ8QW02DGM6TX", "01HJPTHMV9RSFJJWWQ7H3Z5915", "01HJPTHMWPS5EHQFZNBHWS1K3C", "01HJPTHMXDBXE7ENY367M7VTKR", "01HJPTHMY3N22M3M8WWCKJGSND", "01HJPTHN0W0ENEYBR4W694QX2G", "01HJPTHN1KTVZY1PYFGHPTG3YN"]' \
    '--gin.AGENT2_MODEL="custom_model"' \
    '--gin.AGENT1_MODEL="custom_model"' \
    '--gin.BATCH_SIZE=4' \
    '--gin.TAG="init_selftrain_round_1_mistral_mistral_clean"' \
    '--gin.PUSH_TO_DB=True' \
    '--gin.TAG_TO_CHECK_EXISTING_EPISODES="init_selftrain_round_1_mistral_mistral_clean"'
done