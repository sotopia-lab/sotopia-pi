import json
import os

sotopia_data_dir = "ft-data-gpt4-gpt4-easy-2-side-partial/"

ft_data_list = []
for file in os.listdir(sotopia_data_dir):
    with open(os.path.join(sotopia_data_dir, file), 'r') as f:  # 2510
        file_dict = json.load(f)
        output = file_dict["prompt"] + " " + file_dict["result"]
        ft_data_list.append(output)


with open("human-bot-train-gpt4-gpt4-easy-2-side-partial.jsonl", 'w') as f:
    for data in ft_data_list:
        f.write(json.dumps({"text": data}))
        f.write('\n')
