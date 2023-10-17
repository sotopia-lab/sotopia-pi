import json

with open("./data/fastchat-ft-gpt4-gpt4-easy-2-side-partial.json", 'r') as f:
    data = json.load(f)

res = []
for d in data:
    for conv in d['conversations']:
        if conv['from'] == "gpt" and "'action_type': 'speak'" in conv['value']:
            res.append(d)
print(len(res))
with open("./data/fastchat-ft-gpt4-gpt4-easy-2-side-partial-speak.json", 'w') as f:
    json.dump(res, f, indent=4)
