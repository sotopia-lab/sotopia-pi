import json
import os

sotopia_data_dir = "/Users/pamela/Documents/capstone/sotopia-ft-data/ft-data-gpt4-gpt4-easy-2-side-partial"
output_format = """<s>[INST] {prompt} [/INST] {result}</s>"""

ft_data_list = []
for file in os.listdir(sotopia_data_dir):
    with open(os.path.join(sotopia_data_dir, file), 'r') as f:  # 2510
        file_dict = json.load(f)
        output = output_format.format(
            prompt=file_dict["prompt"], result=file_dict["result"])
        ft_data_list.append(output)


with open("fastchat-ft-INST-gp4-gpt4-easy-2-side-partial.jsonl", "w") as f:
    for data in ft_data_list:
        f.write(json.dumps({"text": data}))
        f.write('\n')
