import json
import os
import re
import ast

data_dir = "data-pair-store/" # change this to the directory of parse chat data
full_data = []
TGTAI_FORMAT = """<s>[INST] {user_msg} [/INST] {model_answer} </s>"""

def run_processing(data_dir):
    file_list = os.listdir(data_dir)
    print(len(file_list))
    unusable = 0
    for data_file in file_list:
        try:
            with open(os.path.join(data_dir, data_file), 'r') as f:
                dic = json.load(f)
                prompt = dic["prompt"]
                result = dic["result"]
                format_str = TGTAI_FORMAT.format(user_msg=prompt, model_answer=result)
                full_data.append({'text': format_str})
        except:
            unusable+=1

    print(unusable)
    json_output = json.dumps(full_data, indent=2)
    with open("full-data.jsonl", "w") as f:
        json.dump(full_data, f, indent=4)
