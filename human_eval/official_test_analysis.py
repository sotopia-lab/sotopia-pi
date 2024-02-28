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
import statistics
import ast
import re

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


def get_gpt_score(df, with_scenario=False):
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
            if with_scenario:
                reward_prompt = redis_data['rewards_prompt']
                scenario_match = re.search(r"Scenario:.*", reward_prompt)
                scenario = scenario_match.group(0).replace('Scenario:', '').strip()
                gpt_score[pk]= {'scenario': scenario, 'agent1': score_agent1, 'agent2': score_agent2}
            else:
                gpt_score[pk]= {'agent1': score_agent1, 'agent2': score_agent2}
    return gpt_score


def get_human_score(df, with_scenario=False):
    human_score = defaultdict(list)
    for index, row in df.iterrows():
        agent1_score = {"believability": row['believability_1'], "relationship": row['relationship_1'], "knowledge": row['knowledge_1'], "secret": row['secret_1'], "social_rules": row['social_rules_1'], "financial_and_material_benefits": row['financial_and_material_benefits_1'], "goal": row['goal_1']}
        agent2_score = {"believability": row['believability_2'], "relationship": row['relationship_2'], "knowledge": row['knowledge_2'], "secret": row['secret_2'], "social_rules": row['social_rules_2'], "financial_and_material_benefits": row['financial_and_material_benefits_2'], "goal": row['goal_2']}
        pk = row['pk']
        if with_scenario:
            data = row['data']
            scenario = ast.literal_eval(data)['scenario']
            human_score[pk].append({'scenario': scenario, 'agent1': agent1_score, 'agent2': agent2_score})
        else:
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
        agent1_score = {k: agent1_score[k] / len(human_score[pk]) for k in agent1_score}
        agent2_score = {k: agent2_score[k] / len(human_score[pk]) for k in agent2_score}
        if with_scenario:
            if len(human_score[pk]) <= 1:
                import pdb; pdb.set_trace()
            assert human_score[pk][0]['scenario'] == human_score[pk][1]['scenario']
            mean_human_score[pk] = {'scenario': human_score[pk][0]['scenario'], 'agent1': agent1_score, 'agent2': agent2_score}
        else:
            mean_human_score[pk] = {'agent1': agent1_score, 'agent2': agent2_score}
    return mean_human_score


def pearsonr(dict1, dict2):
    epsilon = 1e-5
    dimensions = ['believability', 'relationship', 'knowledge', 'secret', 'social_rules', 'financial_and_material_benefits', 'goal']
    for dimension in dimensions:
        for agent in ['agent1', 'agent2']:
            x, y = [], []
            for key in dict1.keys():
                x.append(dict1[key][agent][dimension]+epsilon)
                y.append(dict2[key][agent][dimension]+epsilon)
        correlation, p_value = scipy.stats.pearsonr(x, y)
        print(f"{dimension}: {correlation} p_value: {p_value}")
        correlation, p_value = scipy.stats.pearsonr(y, x)
        print(f"{dimension}: {correlation} p_value: {p_value}")



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
    record_score = {'believability': [], 'relationship': [], 'knowledge': [], 'secret': [], 'social_rules': [], 'financial_and_material_benefits': [], 'goal': [], 'overall_score': []}
    std_score = {'believability': 0, 'relationship': 0, 'knowledge': 0, 'secret': 0, 'social_rules': 0, 'financial_and_material_benefits': 0, 'goal': 0}
    average_score = {'believability': 0, 'relationship': 0, 'knowledge': 0, 'secret': 0, 'social_rules': 0, 'financial_and_material_benefits': 0, 'goal': 0}
    for pk_agent_pair in pk_agent_pairs:
        pk, agent_index = pk_agent_pair
        if pk not in score.keys():
            print(f'{pk} is not in human_score')
            continue
        scores_sum = 0 
        count = 0
        for dimension in record_score.keys():
            if dimension != 'overall_score':
                dimension_score = score[pk][agent_index][dimension]
                record_score[dimension].append(dimension_score)
                scores_sum += dimension_score
                count += 1
        if count > 0:
            overall_mean = scores_sum / count
            record_score['overall_score'].append(overall_mean)

    for dimension in record_score.keys():
        std_score[dimension] = statistics.stdev(record_score[dimension])
    for dimension in record_score.keys():
        average_score[dimension] = sum(record_score[dimension]) / len(pk_agent_pairs)
    return average_score, std_score


def list_score(score, pk_agent_pairs, with_scenario=False):
    if with_scenario:
        record_score = {'believability': [], 'relationship': [], 'knowledge': [], 'secret': [], 'social_rules': [], 'financial_and_material_benefits': [], 'goal': [], 'overall_score': [], 'scenario': []}
    else:
        record_score = {'believability': [], 'relationship': [], 'knowledge': [], 'secret': [], 'social_rules': [], 'financial_and_material_benefits': [], 'goal': [], 'overall_score': []}
    for pk_agent_pair in pk_agent_pairs:
        pk, agent_index = pk_agent_pair
        if pk not in score.keys():
            print(f'{pk} is not in human_score')
            continue
        scores_sum = 0 
        count = 0
        for dimension in record_score.keys():
            if dimension != 'overall_score' and dimension != 'scenario':
                dimension_score = score[pk][agent_index][dimension]
                record_score[dimension].append(dimension_score)
                scores_sum += dimension_score
                count += 1
        if count > 0:
            overall_mean = scores_sum / count
            record_score['overall_score'].append(overall_mean)
            if with_scenario:
                scenario = score[pk]['scenario']
                record_score['scenario'].append(scenario)
    return record_score


def average_scenario_score(human_score, scenarios):
    scenario_scores = {'believability': [], 'relationship': [], 'knowledge': [], 'secret': [], 'social_rules': [], 'financial_and_material_benefits': [], 'goal': [], 'overall_score': []}
    for tgt_scenario in scenarios:
        scenario_score = {'believability': [], 'relationship': [], 'knowledge': [], 'secret': [], 'social_rules': [], 'financial_and_material_benefits': [], 'goal': [], 'overall_score': []}
        for idx, src_scenario in enumerate(human_score['scenario']):
            # get average score on all dimensions for the same scenario
            if src_scenario == tgt_scenario:
                for dimension in scenario_score.keys():
                    scenario_score[dimension].append(human_score[dimension][idx])
        for dimension in scenario_scores.keys():
            scenario_scores[dimension].append(sum(scenario_score[dimension])/len(scenario_score[dimension]))

    return scenario_scores



def paired_t_test(model_name1, model_name2, csv_name_dict):
    # getthe average score for each scenario data and pair them together
    df1 = pd.read_csv(csv_name_dict[model_name1])
    df2 = pd.read_csv(csv_name_dict[model_name2])
    human_score1 = get_human_score(df1, with_scenario=True)
    human_score2 = get_human_score(df2, with_scenario=True)

    pk_agent_pairs_1 = collect_pk_agent_pairs(directory_name_dict[model_name1], model_side_dict[model_name1])
    pk_agent_pairs_2 = collect_pk_agent_pairs(directory_name_dict[model_name2], model_side_dict[model_name2])
    human_score1 = list_score(human_score1, pk_agent_pairs_1, with_scenario=True)
    human_score2 = list_score(human_score2, pk_agent_pairs_2, with_scenario=True)

    scenario1 = set(human_score1['scenario'])
    scenario2 = set(human_score2['scenario'])
    shared_scenarios = list(scenario1.intersection(scenario2))
    print(len(shared_scenarios))

    scenario_mean_score1 = average_scenario_score(human_score1, shared_scenarios)
    scenario_mean_score2 = average_scenario_score(human_score2, shared_scenarios)

    tot_scenario_mean_score1 = {}
    tot_scenario_mean_score2 = {}
    for dimension in scenario_mean_score1.keys():
        tot_scenario_mean_score1[dimension] = sum(scenario_mean_score1[dimension])/len(scenario_mean_score1[dimension])
    for dimension in scenario_mean_score2.keys():
        tot_scenario_mean_score2[dimension] = sum(scenario_mean_score2[dimension])/len(scenario_mean_score2[dimension])

    print('{}: {}'.format(model_name1, tot_scenario_mean_score1))
    print('{}: {}'.format(model_name2, tot_scenario_mean_score2))

    paired_t_test_result = []
    for key in scenario_mean_score1.keys():
        t, p = scipy.stats.ttest_rel(scenario_mean_score1[key], scenario_mean_score2[key])
        #print(f"{key}: t: {t}, p: {p}")
        paired_t_test_result.append((t, p))
    latex_table_format = " & ".join([f"{t:.2f} ({p:.3f})" for t, p in paired_t_test_result])
    print(latex_table_format)
    print('='*50)
    return


if __name__ == '__main__':
    model_name = 'BC'
    csv_name_dict = {
        'gpt4': './gpt4_final.csv',
        'gpt3.5': './gpt3.5_final.csv',
        'mistral-instruct': './mistral-instruct_final.csv',
        'SR': './SR_final.csv',
        'BC': './BC_final.csv',
        'BC+SR': './BC+SR_final.csv',
    }
    directory_name_dict = {
        'gpt4': './otree_project/sotopia_official_study/GPT3.5-GPT4',
        'gpt3.5': './otree_project/sotopia_official_study/GPT3.5-GPT3.5',
        'mistral-instruct': './otree_project/sotopia_official_study/GPT3.5-MistralInstruct',
        'SR': './otree_project/sotopia_official_study/GPT3.5-SR',
        'BC': './otree_project/sotopia_official_study/GPT3.5-BC',
        'BC+SR': './otree_project/sotopia_official_study/GPT3.5-BC-SR'
    }
    model_side_dict = {
        'gpt4': 'gpt-4',
        'gpt3.5': 'gpt-3.5-turbo',
        'mistral-instruct': 'custom_model',
        'SR': 'custom_model',
        'BC': 'custom_model',
        'BC+SR': 'custom_model',
    }

    paired_t_test('BC+SR', 'gpt4', csv_name_dict)
    paired_t_test('BC+SR', 'gpt3.5', csv_name_dict)
    paired_t_test('BC+SR', 'mistral-instruct', csv_name_dict)
    paired_t_test('BC+SR', 'SR', csv_name_dict)
    paired_t_test('BC+SR', 'BC', csv_name_dict)

    df = pd.read_csv(csv_name_dict[model_name])
    gpt_score = get_gpt_score(df)
    human_score = get_human_score(df)
    pk_agent_pairs = collect_pk_agent_pairs(directory_name_dict[model_name], model_side_dict[model_name])
    average_human_score, std_human_score = average_score(human_score, pk_agent_pairs)
    average_gpt_score, std_gpt_score = average_score(gpt_score, pk_agent_pairs)
    pearsonr(gpt_score, human_score)
    print(f"average_human_score: {average_human_score}")
    print(f"average_gpt_score: {average_gpt_score}")
    print(f"std_human_score: {std_human_score}")
    print(f"std_gpt_score: {std_gpt_score}")

