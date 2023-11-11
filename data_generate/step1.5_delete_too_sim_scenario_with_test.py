import csv
import pandas as pd
import evaluate
from tqdm import tqdm

bertscore = evaluate.load("bertscore")

def convert_string_to_list(string):
    # Assuming the list is separated by commas and without extra spaces
    return string.strip('[]').split(',')

def is_similar_to_any(text_tgt, list_src, similarity_threshold):
    scores = bertscore.compute(predictions=[text_tgt]*len(list_src), references=list_src, lang="en")
    print(scores['f1'])
    return any(score > similarity_threshold for score in scores['f1'])

tgt_df = pd.read_csv(
    'env_filtered.csv',
    converters={'agent_goals': convert_string_to_list}
    )

tgt_scenario_list = tgt_df['scenario'].tolist()

src_df = pd.read_csv(
    'HardEnvProfile.csv',
    converters={'agent_goals': convert_string_to_list}
    )

src_scenario_list = src_df['scenario'].tolist()

similarity_threshold = 0.875  # Adjust as needed

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
