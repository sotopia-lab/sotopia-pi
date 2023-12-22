import jsonlines
import csv
from tqdm import tqdm

def collect_social_iqa(inspirational_prompt_data):
    with jsonlines.open('./social_src/social_iqa_train.jsonl', 'r') as f:
        social_iqa_dataset = list(f)
    for data in social_iqa_dataset:
        inspirational_prompt_data.append({'prompt': data['context'], 'source': 'social_iqa'})
    return inspirational_prompt_data


def collect_normbank(inspirational_prompt_data):
    rows = []
    with open("./social_src/NormBank.csv", 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            inspirational_prompt_data.append({'prompt': row[1], 'source': 'normbank'})
    return inspirational_prompt_data


def collect_social_chemistry(inspirational_prompt_data):
    rows = []
    with open("./social_src/social-chem-101.v1.0.tsv", 'r') as file:
        csvreader = csv.reader(file, delimiter="\t")
        header = next(csvreader)
        for row in csvreader:
            inspirational_prompt_data.append({'prompt': row[-6], 'source': 'normbank'})
    return inspirational_prompt_data

def collect_persuation_for_good(inspirational_prompt_data):
    from convokit import Corpus, download
    corpus = Corpus(filename=download("persuasionforgood-corpus"))
    import pdb; pdb.set_trace()

def delete_sotopia_data(inspirational_prompt_data):
    sotopia_prompts = []
    with open("./social_src/inspirational_prompt_for_sotopia.csv", 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            sotopia_prompts.append(row[0])
    for inspirational_prompt in tqdm(inspirational_prompt_data):
        if inspirational_prompt['prompt'] in sotopia_prompts:
            inspirational_prompt_data.remove(inspirational_prompt)
    print(len(inspirational_prompt_data))
    return inspirational_prompt_data


inspirational_prompt_data = []
#inspirational_prompt_data = collect_persuation_for_good(inspirational_prompt_data)
inspirational_prompt_data = collect_social_chemistry(inspirational_prompt_data)
inspirational_prompt_data = collect_social_iqa(inspirational_prompt_data)
inspirational_prompt_data = collect_normbank(inspirational_prompt_data)
inspirational_prompt_data = delete_sotopia_data(inspirational_prompt_data)

fieldnames = inspirational_prompt_data[0].keys()

# Write to a CSV file
with open('./social_src/inspirational_prompt.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # Write the header (optional, but usually a good idea)
    writer.writeheader()
    for row in inspirational_prompt_data:
        writer.writerow(row)
