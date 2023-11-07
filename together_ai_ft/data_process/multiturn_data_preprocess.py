import json
import os

sotopia_data_dir = "/Users/pamela/Documents/capstone/sotopia-ft-data/GPT4-4_Redis_Easy_No_Filter"

together_data_template = """<s>[INST] {user_msg} [/INST] {assistant_msg} </s>"""

lines = []
for file in os.listdir(sotopia_data_dir):
    with open(os.path.join(sotopia_data_dir, file), 'r') as f:
        file_dict = json.load(f)
        text = together_data_template.format(
            user_msg=file_dict["prompt"], assistant_msg=file_dict["result"])
        lines.append(text)

with open("together-ft-gpt4-gpt4-easy-no-filter.jsonl", 'w') as f:
    for line in lines:
        f.write(json.dumps({"text": line}))
        f.write('\n')
