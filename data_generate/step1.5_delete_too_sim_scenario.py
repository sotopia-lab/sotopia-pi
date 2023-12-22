import csv
import pandas as pd
import evaluate
from tqdm import tqdm
from transformers import BertTokenizer, BertModel
import torch
import torch.nn.functional as F

bertscore = evaluate.load("bertscore")

def convert_string_to_list(string):
    # Assuming the list is separated by commas and without extra spaces
    return string.strip('[]').split(',')

def is_similar_to_any(text_tgt, list_src, similarity_threshold):
    scores = bertscore.compute(predictions=[text_tgt]*len(list_src), references=list_src, lang="en")
    print(scores['f1'])
    return any(score > similarity_threshold for score in scores['f1'])

def encode_sentence(model, tokenizer, sentence):
    # Tokenize and encode the sentence
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
    # Get the model's output
    with torch.no_grad():  # Disable gradient calculations for efficiency
        outputs = model(**inputs)
    # Extract the embeddings from the last hidden layer
    embeddings = outputs.last_hidden_state
    return embeddings.mean(dim=1, keepdim=False)  # Return the mean of the embeddings

def max_cos_sim(target_emb, src_embs):
    # Compute cosine similarity with each source embedding
    similarities = [F.cosine_similarity(target_emb.unsqueeze(0), src_emb.unsqueeze(0), dim=1) for src_emb in src_embs]
    # Return the maximum similarity
    import pdb; pdb.set_trace()
    return max(similarities)


tgt_df = pd.read_csv(
    'env_filtered_scenario_unique_social_goal_reasonable_different_from_testset_part1.csv',
    converters={'agent_goals': convert_string_to_list}
    )

tgt_scenario_list = tgt_df['scenario'].tolist()

src_df = pd.read_csv(
    'HardEnvProfile.csv',
    converters={'agent_goals': convert_string_to_list}
    )

src_scenario_list = src_df['scenario'].tolist()

sim_upper_threshold = 0.875  # Adjust as needed
sim_lower_threshold = 0.750  # Adjust as needed

model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)
model.eval()  # Set the model to evaluation mode

src_embeddings = []
tgt_embeddings = []
for sentence in src_scenario_list:
    src_embeddings.append(encode_sentence(model, tokenizer, sentence))

for sentence in tgt_scenario_list:
    tgt_embeddings.append(encode_sentence(model, tokenizer, sentence))

max_similarities = [max_cos_sim(tgt_emb, src_embeddings) for tgt_emb in tgt_embeddings]
import pdb; pdb.set_trace()

dropped_tgt_scenario_list = []
for text_tgt in tqdm(tgt_scenario_list):
    if is_similar_to_any(text_tgt, src_scenario_list, similarity_threshold):
        dropped_tgt_scenario_list.append(text_tgt)
        #print(text_tgt)
        #print("===")
        #for text_src in src_scenario_list:
        #    print(text_src)

# iterate the df and drop the rows
for text_tgt in dropped_tgt_scenario_list:
    tgt_df = tgt_df[tgt_df["scenario"] != text_tgt]

# save tgt_df to csv
tgt_df.to_csv('env_filtered_filtered_0.875.csv', index=False)
