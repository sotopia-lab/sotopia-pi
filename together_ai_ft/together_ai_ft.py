import together
import os

together.api_key = ""


data_path = "/Users/pamela/Documents/capstone/sotopia-ft-data/human-bot-train-gpt4-gpt4-easy-partial.jsonl"
model_type = "togethercomputer/llama-2-13b-chat"

resp = together.Files.check(file=data_path, model=model_type)
resp = together.Files.upload(file=data_path, model=model_type)
file_id = resp["id"]
# print(file_id)
# files_list = together.Files.list()
# print(files_list['data'])

resp = together.Finetune.create(
    # training_file = files_list['data'][0]['id'],
    training_file=file_id,
    model=model_type,
    n_epochs=1,
    n_checkpoints=1,
    batch_size=8,
    learning_rate=5e-5,
    suffix='sotopia-finetune-GPT4+GPT4-clean-tag-1',
    wandb_api_key='eca44f65849afa1cc146c22631b0b5001ccd24d7',
)

fine_tune_id = resp['id']
print(resp)
