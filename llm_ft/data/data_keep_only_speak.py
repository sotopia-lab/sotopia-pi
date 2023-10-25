import json

INPUT_PATH = "fastchat-ft-gpt4-gpt4-easy-2-side-partial.json"
OUTPUT_PATH = "fastchat-ft-gpt4-gpt4-easy-2-side-partial-speak.json"

with open(INPUT_PATH, 'r') as f:
    data = json.load(f)

res = []
for d in data:
    for conv in d['conversations']:
        if conv['from'] == "gpt" and "'action_type': 'speak'" in conv['value']:
            res.append(d)

with open(OUTPUT_PATH, 'w') as f:
    json.dump(res, f, indent=4)
