import json
import transformers

with open("fastchat-ft-gpt4-gpt4-easy-2-side-partial-speak.json", 'r') as f:
    data = json.load(f)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    'meta-llama/Llama-2-13b-chat-hf',
    padding = False,
    truncation = False,
    token="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",
    )
    
res = []
for d in data:
    for conv in d['conversations']:
        if conv['from'] == "human":
            input_ids = tokenizer(conv['value'])
            if len(input_ids) <= 2048:
                res.append(d)
                
with open("fastchat-ft-gpt4-gpt4-easy-2-side-partial-speak-no-long.json", 'w') as f:
    json.dump(res, f, indent=4)