import json

with open("./fastchat-ft-gp4-gpt4-easy-truncated.json", "r") as f:
    data = json.load(f)

result = []
for dp in data:
    new_dp = {}
    convs = dp["conversations"]
    new_dp["instruction"] = convs[0]["value"]
    new_dp["input"] = ""
    new_dp["output"] = convs[1]["value"]

    result.append(new_dp)

with open("../data/fastchat-ft-gp4-gpt4-easy-truncated.json", "w") as f:
    json.dump(result, f, indent=4)
