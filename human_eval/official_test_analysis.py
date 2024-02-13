import csv
import pandas as pd
import math
from rejson import Client, Path
import json
import redis
import os
import scipy.stats
from collections import defaultdict
from tqdm import tqdm

redis_host = 'tiger.lti.cs.cmu.edu'
redis_port = 6388
redis_password = 'aclkasjf29qwrUOIO'

hard_environment_pk = [
    "01H7VFHNNYH3W0VRWVY178K2TK",
    "01H7VFHPDZVVCDZR3AARA547CY",
    "01H7VFHP8AN5643B0NR0NP00VE",
    "01H7VFHNN7XTR99319DS8KZCQM",
    "01H7VFHN5WVC5HKKVBHZBA553R",
    "01H7VFHNF4G18PC9JHGRC8A1R6",
    "01H7VFHN7WJK7VWVRZZTQ6DX9T",
    "01H7VFHN7A1ZX5KSMT2YN9RXC4",
    "01H7VFHNV13MHN97GAH73E3KM8",
    "01H7VFHPSWGDGEYRP63H2DJKV0",
    "01H7VFHPS5WJW2694R1MNC8JFY",
    "01H7VFHQ11NAMZS4A2RDGDB01V",
    "01H7VFHPQQQY6H4DNC6NBQ8XTG",
    "01H7VFHN9W0WAFZCBT09PKJJNK",
]

def get_redisjson_value(r, key):
    try:
        return r.jsonget(key, Path.rootPath())
    except Exception as e:
        print(f"Could not retrieve JSON for key {key}: {e}")
        return None

def get_redisjson_key_tag_value(r, key):
    try:
        # Fetch only the 'tag' field from the JSON document
        return r.jsonget(key, Path('.tag'))
    except Exception as e:
        print(f"Could not retrieve tag for key {key}: {e}")
        return None
    
def fetch_tag_field(r, key):
    try:
        # Attempt to fetch only the 'tag' field from the JSON document
        tag_value = r.jsonget(key, Path('.tag'))
        return key, tag_value
    except Exception as e:
        print(f"Could not retrieve tag for key {key}: {e}")
        return key, None
    
def get_tag_score(tag, model_name, subpart='hard'):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    gpt_score = {}
    futures = []

    r = Client(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
    keys = r.keys('*EpisodeLog*')

    with ThreadPoolExecutor(max_workers=20) as executor:
        for key in keys:
            futures.append(executor.submit(fetch_tag_field, r, key))

    redis_tags = []
    pk_agent_pairs = []
    for future in as_completed(futures):
        key, redis_tag = future.result()
        redis_tags.append(redis_tag)
        if redis_tag == tag:
            redis_data = get_redisjson_value(r, key)
            if subpart == 'hard' and redis_data['environment'] not in hard_environment_pk:
                continue
            if redis_data is not None:
                models = redis_data['models']
                if models[1] == model_name:
                    pk = key.split(':')[-1]
                    pk_agent_pairs.append((pk, redis_data['environment'], 'agent1'))
                if models[2] == model_name:
                    pk = key.split(':')[-1]
                    pk_agent_pairs.append((pk, redis_data['environment'], 'agent2'))
                # Safely access 'rewards' and its last elements for both agents
                score_agent1 = redis_data.get('rewards', [[None]])[0][-1]
                score_agent2 = redis_data.get('rewards', [[None]])[-1][-1]
                if score_agent1 is not None and score_agent2 is not None:
                    pk = key.split(':')[-1]
                    gpt_score[pk] = {'env_pk': redis_data['environment'], 'agent1': score_agent1, 'agent2': score_agent2}
    return gpt_score, pk_agent_pairs


def get_gpt_score(df):
    pks = df['pk'].tolist()
    gpt_score = {}
    r = Client(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
    keys = r.keys('*')
    for key in keys:
        pk = key.split(':')[-1]
        if pk in pks:
            redis_data = get_redisjson_value(r, key)
            score_agent1 = redis_data['rewards'][0][-1]
            score_agent2 = redis_data['rewards'][-1][-1]
            gpt_score[pk]= {'agent1': score_agent1, 'agent2': score_agent2}
    return gpt_score




def get_human_score(df):
    human_score = defaultdict(list)
    for index, row in df.iterrows():
        agent1_score = {"believability": row['believability_1'], "relationship": row['relationship_1'], "knowledge": row['knowledge_1'], "secret": row['secret_1'], "social_rules": row['social_rules_1'], "financial_and_material_benefits": row['financial_and_material_benefits_1'], "goal": row['goal_1']}
        agent2_score = {"believability": row['believability_2'], "relationship": row['relationship_2'], "knowledge": row['knowledge_2'], "secret": row['secret_2'], "social_rules": row['social_rules_2'], "financial_and_material_benefits": row['financial_and_material_benefits_2'], "goal": row['goal_2']}
        pk = row['pk']
        human_score[pk].append({'agent1': agent1_score, 'agent2': agent2_score})

    mean_human_score = {}
    # get the average score for each pair of human_score
    for pk in human_score.keys():
        agent1_score = {"believability": 0, "relationship": 0, "knowledge": 0, "secret": 0, "social_rules": 0, "financial_and_material_benefits": 0, "goal": 0}
        agent2_score = {"believability": 0, "relationship": 0, "knowledge": 0, "secret": 0, "social_rules": 0, "financial_and_material_benefits": 0, "goal": 0}
        for score in human_score[pk]:
            try:
                agent1_score = {k: agent1_score[k] + int(score['agent1'][k]) for k in agent1_score}
                agent2_score = {k: agent2_score[k] + int(score['agent2'][k]) for k in agent2_score}
            except:
                print(f"pk: {pk}, score: {score}")
                import pdb; pdb.set_trace()
        print(len(human_score[pk]))
        agent1_score = {k: agent1_score[k] / len(human_score[pk]) for k in agent1_score}
        agent2_score = {k: agent2_score[k] / len(human_score[pk]) for k in agent2_score}
        mean_human_score[pk] = {'agent1': agent1_score, 'agent2': agent2_score}
    return mean_human_score


def pearsonr(dict1, dict2):
    dimensions = ['believability', 'relationship', 'knowledge', 'secret', 'social_rules', 'financial_and_material_benefits', 'goal']
    for dimension in dimensions:
        for agent in ['agent1', 'agent2']:
            x, y = [], []
            for key in dict1.keys():
                x.append(dict1[key][agent][dimension])
                y.append(dict2[key][agent][dimension])
        correlation = scipy.stats.pearsonr(x, y)[0]
        print(f"{dimension}: {correlation}")
        correlation = scipy.stats.pearsonr(y, x)[0]
        print(f"{dimension}: {correlation}")


def collect_pk_agent_pairs(directory, target_model):
    pk_agent_pairs = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as f:
                data = json.load(f)
                models = data['models']
                if models[1] == target_model:
                    pk_agent_pairs.append((filename.split('.')[0], 'agent1'))
                if models[2] == target_model:
                    pk_agent_pairs.append((filename.split('.')[0], 'agent2'))
    return pk_agent_pairs


def average_score(score, pk_agent_pairs):
    average_score = {'believability': 0, 'relationship': 0, 'knowledge': 0, 'secret': 0, 'social_rules': 0, 'financial_and_material_benefits': 0, 'goal': 0, 'overall_score': 0}
    for pk_agent_pair in pk_agent_pairs:
        pk, env_pk,  agent_index = pk_agent_pair
        if pk not in score.keys():
            print('{} is not in human_score'.format(pk))
            continue
        for dimension in score[pk][agent_index].keys():
            average_score[dimension] += score[pk][agent_index][dimension]
    for dimension in average_score.keys():
        average_score[dimension] /= len(pk_agent_pairs)
    average_score['overall_score'] = sum(average_score.values()) / len(average_score)
    return average_score


if __name__ == '__main__':
    complete_gpt_score, complete_pk_agent_pairs = get_tag_score('gpt-4_gpt-3.5-turbo_v0.0.1_clean', 'gpt-4')
    #complete_gpt_score, complete_pk_agent_pairs = get_tag_score('sft-selftrain-round-1-filtered-top-4_checkpoint_improve-0_epoch-5_gpt-3.5-turbo_test', 'custom_model')
    # save the complete_gpt_score
    with open('complete_gpt_score.json', 'w') as f:
        json.dump(complete_gpt_score, f)
    with open('complete_pk_agent_pairs.json', 'w') as f:
        json.dump(complete_pk_agent_pairs, f)
    average_complete_gpt_score = average_score(complete_gpt_score, complete_pk_agent_pairs)
    print(f"average_complete_gpt_score: {average_complete_gpt_score}")
    import pdb; pdb.set_trace()
    #df = pd.read_csv('./mistral-instruct_final.csv')
    #df = pd.read_csv('./self-train-round3_final.csv')
    #df = pd.read_csv('./self-train-round2_final.csv')
    #df = pd.read_csv('./self-train-round1_final.csv')
    #df = pd.read_csv('./BC-self-train-round1_final.csv')
    #df = pd.read_csv('./BC_final.csv')
    #df = pd.read_csv('./mistral-instruct_final.csv')
    df = pd.read_csv('./gpt4_final.csv')
    gpt_score = get_gpt_score(df)
    human_score = get_human_score(df)
    pearsonr(gpt_score, human_score)
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-GPT3.5-New', 'gpt-3.5-turbo')
    pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-GPT4-New', 'gpt-4')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-MistralInstruct', 'gpt-3.5-turbo')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-SelfTrain-Round3', 'custom_model')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-SelfTrain-Round2', 'custom_model_selftrain')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-SelfTrain-Round1', 'gpt-3.5-turbo')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-BC-SelfTrain-Round1', 'custom_model')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-BC-Pure', 'custom_model')
    #pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-MistralInstruct', 'custom_model')
    print(f"pk_agent_pairs: {len(pk_agent_pairs)}")
    average_human_score = average_score(human_score, pk_agent_pairs)
    average_gpt_score = average_score(gpt_score, pk_agent_pairs)
    print(f"average_human_score: {average_human_score}")
    print(f"average_gpt_score: {average_gpt_score}")