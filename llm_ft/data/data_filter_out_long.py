import json
import transformers

INPUT_PATH = "fastchat-ft-gpt4-gpt4-easy-2-side-partial-speak.json"
OUTPUT_PATH = "fastchat-ft-gpt4-gpt4-easy-2-side-partial-speak-no-long.json"
MODEL_CHECKPOINT = "meta-llama/Llama-2-13b-chat-hf"
HF_TOKEN = "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"

with open(INPUT_PATH, 'r') as f:
    data = json.load(f)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    MODEL_CHECKPOINT,
    padding = False,
    truncation = False,
    token=HF_TOKEN,
    )
    
res = []
for d in data:
    for conv in d['conversations']:
        if conv['from'] == "human":
            input_ids = tokenizer(conv['value'])
            if len(input_ids) <= 2048:
                res.append(d)
                
with open(OUTPUT_PATH, 'w') as f:
    json.dump(res, f, indent=4)