import json
import os

sotopia_data_dir = "/Users/pamela/Documents/capstone/sotopia-ft-data/ft-data-gpt4-gpt4-easy-2-side-partial"

ft_data_list = []
count = 0
for file in os.listdir(sotopia_data_dir):
    with open(os.path.join(sotopia_data_dir, file), 'r') as f:
        file_dict = json.load(f)
        fastchat_dict = {"id": f"identity_{count}", "conversations": []}
        fastchat_dict["conversations"].append(
            {"from": "human", "value": file_dict["prompt"]})
        fastchat_dict["conversations"].append(
            {"from": "gpt", "value": file_dict["result"]})
        ft_data_list.append(fastchat_dict)
        count += 1

with open("fastchat-ft-gp4-gpt4-easy-2-side-partial.json", "w") as f:
    f.write(json.dumps(ft_data_list, indent=4))