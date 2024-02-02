import csv
import pandas as pd
import math
from rejson import Client, Path
import json
import redis
import os
import scipy.stats
from collections import defaultdict

redis_host = 'server_name'
redis_port  = "port_num"
redis_password = 'password'



selected_columns = [
    'player.pk',
    'player.data',
    'player.prolific_id',
    'player.believability_1',
    'player.believability_reasoning_1',
    'player.relationship_1',
    'player.relationship_reasoning_1',
    'player.knowledge_1',
    'player.knowledge_reasoning_1',
    'player.secret_1',
    'player.secret_reasoning_1',
    'player.social_rules_1',
    'player.social_rules_reasoning_1',
    'player.financial_and_material_benefits_1',
    'player.financial_and_material_benefits_reasoning_1',
    'player.goal_1',
    'player.goal_reasoning_1',
    'player.believability_2',
    'player.believability_reasoning_2',
    'player.relationship_2',
    'player.relationship_reasoning_2',
    'player.knowledge_2',
    'player.knowledge_reasoning_2',
    'player.secret_2',
    'player.secret_reasoning_2',
    'player.social_rules_2',
    'player.social_rules_reasoning_2',
    'player.financial_and_material_benefits_2',
    'player.financial_and_material_benefits_reasoning_2',
    'player.goal_2',
    'player.goal_reasoning_2'
]


def filter_out_useless_column(df):
    df = df[selected_columns]
    return df


def filter_out_useless_data(df):
    for col in selected_columns:
        if col in df.keys():
            df = df[df[col].notna()]
    return df



def get_redisjson_value(r, key):
    try:
        return r.jsonget(key, Path.rootPath())
    except Exception as e:
        print(f"Could not retrieve JSON for key {key}: {e}")
        return None


def get_gpt_score(df):
    pks = df['player.pk'].tolist()

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
        agent1_score = {"believability": row['player.believability_1'], "relationship": row['player.relationship_1'], "knowledge": row['player.knowledge_1'], "secret": row['player.secret_1'], "social_rules": row['player.social_rules_1'], "financial_and_material_benefits": row['player.financial_and_material_benefits_1'], "goal": row['player.goal_1']}
        agent2_score = {"believability": row['player.believability_2'], "relationship": row['player.relationship_2'], "knowledge": row['player.knowledge_2'], "secret": row['player.secret_2'], "social_rules": row['player.social_rules_2'], "financial_and_material_benefits": row['player.financial_and_material_benefits_2'], "goal": row['player.goal_2']}
        pk = row['player.pk']
        human_score[pk].append({'agent1': agent1_score, 'agent2': agent2_score})

    mean_human_score = {}
    # get the average score for each pair of human_score
    for pk in human_score.keys():
        agent1_score = {"believability": 0, "relationship": 0, "knowledge": 0, "secret": 0, "social_rules": 0, "financial_and_material_benefits": 0, "goal": 0}
        agent2_score = {"believability": 0, "relationship": 0, "knowledge": 0, "secret": 0, "social_rules": 0, "financial_and_material_benefits": 0, "goal": 0}
        for score in human_score[pk]:
            agent1_score = {k: agent1_score[k] + score['agent1'][k] for k in agent1_score}
            agent2_score = {k: agent2_score[k] + score['agent2'][k] for k in agent2_score}
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


def average_score(human_score, pk_agent_pairs):
    average_score = {}
    for pk_agent_pair in pk_agent_pairs:
        pk, agent_index = pk_agent_pair
        if pk not in human_score.keys():
            print('{} is not in human_score'.format(pk))
            continue
        for dimension in human_score[pk][agent_index].keys():
            if dimension not in average_score:
                average_score[dimension] = 0
            average_score[dimension] += human_score[pk][agent_index][dimension]
    for dimension in average_score.keys():
        average_score[dimension] /= len(pk_agent_pairs)
    average_score['overall_score'] = sum(average_score.values()) / len(average_score)
    return average_score
    

if __name__ == '__main__':
    df = pd.read_csv('./0201_without_bad_examples_filtered.csv')
    gpt_score = get_gpt_score(df)
    human_score = get_human_score(df)
    pearsonr(gpt_score, human_score)
    GPT35_pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-GPT3.5-New', 'gpt-3.5-turbo')
    GPT4_pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-GPT4-New', 'gpt-4')
    mistral_instruct_pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-MistralInstruct', 'custom_model')
    sotopia_pi_pk_agent_pairs = collect_pk_agent_pairs('./otree_project/sotopia_official_study/GPT3.5-SelfTrain-Round2', 'custom_model_selftrain')
    print(f"GPT3.5-GPT3.5-New: {len(GPT35_pk_agent_pairs)}")
    print(f"GPT3.5-GPT4-New: {len(GPT4_pk_agent_pairs)}")
    print(f"GPT3.5-MistralInstruct: {len(mistral_instruct_pk_agent_pairs)}")
    print(f"GPT3.5-Sotopia_PI: {len(sotopia_pi_pk_agent_pairs)}")
    average_score_GPT35 = average_score(human_score, GPT35_pk_agent_pairs)
    average_score_GPT4 = average_score(human_score, GPT4_pk_agent_pairs)
    average_score_mistral_instruct = average_score(human_score, mistral_instruct_pk_agent_pairs)
    average_score_sotopia_pi = average_score(human_score, sotopia_pi_pk_agent_pairs)
    print(f"average_score_GPT35: {average_score_GPT35}")
    print(f"average_score_GPT4: {average_score_GPT4}")
    print(f"average_score_mistral_instruct: {average_score_mistral_instruct}")
    print(f"average_score_sotopia_pi: {average_score_sotopia_pi}")

