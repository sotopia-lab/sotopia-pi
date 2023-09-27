import together
import os

resp = together.Files.upload(file="together_ai_data.jsonl")
file_id = resp["id"]
files_list = together.Files.list()


resp = together.Finetune.create(
    training_file = files_list['data'][0]['id'],
    model = 'togethercomputer/llama-2-7b-chat',
    n_epochs = 3,
    n_checkpoints = 1,
    batch_size = 4,
    learning_rate = 1e-5,
    suffix = 'test-finetune',
    wandb_api_key = '972035264241fb0f6cc3cab51a5d82f47ca713db',
)

fine_tune_id = resp['id']
print(resp)

