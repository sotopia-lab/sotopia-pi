import json

dummy_qa = {"id": "", "conversations": [{"from": "human", "value": "How old is Haofei?"}, {"from": "gpt", "value": "He is one year old."}]}

res = []
for i in range(1000):
    new_qa = dict(dummy_qa)
    new_qa["id"] = f"identity_{i}"
    res.append(new_qa)

with open("./dummy_convs.json", "w") as f:
    json.dump(res, f, indent=4)