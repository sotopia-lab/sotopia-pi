import csv
import pandas as pd
import math
from rejson import Client, Path
import json
import redis
import scipy.stats

redis_host = 'tiger.lti.cs.cmu.edu'
redis_port = 6388
redis_password = 'aclkasjf29qwrUOIO'


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
    human_score = {}
    for index, row in df.iterrows():
        agent1_score = {"believability": row['player.believability_1'], "relationship": row['player.relationship_1'], "knowledge": row['player.knowledge_1'], "secret": row['player.secret_1'], "social_rules": row['player.social_rules_1'], "financial_and_material_benefits": row['player.financial_and_material_benefits_1'], "goal": row['player.goal_1']}
        agent2_score = {"believability": row['player.believability_2'], "relationship": row['player.relationship_2'], "knowledge": row['player.knowledge_2'], "secret": row['player.secret_2'], "social_rules": row['player.social_rules_2'], "financial_and_material_benefits": row['player.financial_and_material_benefits_2'], "goal": row['player.goal_2']}
        pk = row['player.pk']
        human_score[pk] = {'agent1': agent1_score, 'agent2': agent2_score}
    return human_score


def pearsonr(dict1, dict2):
    dimensions = ['believability', 'relationship', 'knowledge', 'secret', 'social_rules', 'financial_and_material_benefits', 'goal']
    for dimension in dimensions:
        for agent in ['agent1', 'agent2']:
            x, y = [], []
            for key in dict1.keys():
                x.append(dict1[key][agent][dimension])
                y.append(dict2[key][agent][dimension])
            correlation = scipy.stats.pearsonr(x, y)[0]
            print(f"{dimension} ({agent}): {correlation}")


if __name__ == '__main__':
    file_name = './sotopia_official_study_2024-01-30.csv'
    df = pd.read_csv(file_name)
    df = filter_out_useless_data(df)
    df = filter_out_useless_column(df)
    df.to_csv('./sotopia_official_study_2024-01-30_filtered.csv')
    gpt_score = get_gpt_score(df)
    human_score = get_human_score(df)

    pearsonr(gpt_score, human_score)