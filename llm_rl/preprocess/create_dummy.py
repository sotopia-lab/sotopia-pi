import json

dummy_qa =   {
    "instruction": "How old is Haofei? ",
    "input": "",
    "output": "Haofei is one year old. "
  }

res = []
for i in range(1000):
    new_qa = dict(dummy_qa)
    res.append(new_qa)

with open("../data/dummy_convs.json", "w") as f:
    json.dump(res, f, indent=4)