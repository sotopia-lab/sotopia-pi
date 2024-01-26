import csv
import pandas as pd
columns_to_filter = [
    'sotopia_pilot_study.1.player.prolific_id',
    'sotopia_pilot_study.1.player.believability_1',
    'sotopia_pilot_study.1.player.believability_reasoning_1',
    'sotopia_pilot_study.1.player.relationship_1',
    'sotopia_pilot_study.1.player.relationship_reasoning_1',
    'sotopia_pilot_study.1.player.knowledge_1',
    'sotopia_pilot_study.1.player.knowledge_reasoning_1',
    'sotopia_pilot_study.1.player.secret_1',
    'sotopia_pilot_study.1.player.secret_reasoning_1',
    'sotopia_pilot_study.1.player.social_rules_1',
    'sotopia_pilot_study.1.player.social_rules_reasoning_1',
    'sotopia_pilot_study.1.player.financial_and_material_benefits_1',
    'sotopia_pilot_study.1.player.financial_and_material_benefits_reasoning_1',
    'sotopia_pilot_study.1.player.goal_1',
    'sotopia_pilot_study.1.player.goal_reasoning_1',
    'sotopia_pilot_study.1.player.believability_2',
    'sotopia_pilot_study.1.player.believability_reasoning_2',
    'sotopia_pilot_study.1.player.relationship_2',
    'sotopia_pilot_study.1.player.relationship_reasoning_2',
    'sotopia_pilot_study.1.player.knowledge_2',
    'sotopia_pilot_study.1.player.knowledge_reasoning_2',
    'sotopia_pilot_study.1.player.secret_2',
    'sotopia_pilot_study.1.player.secret_reasoning_2',
    'sotopia_pilot_study.1.player.social_rules_2',
    'sotopia_pilot_study.1.player.social_rules_reasoning_2',
    'sotopia_pilot_study.1.player.financial_and_material_benefits_2',
    'sotopia_pilot_study.1.player.financial_and_material_benefits_reasoning_2',
    'sotopia_pilot_study.1.player.goal_2',
    'sotopia_pilot_study.1.player.goal_reasoning_2'
]


def filter_out_useless_data(df):
    for col in columns_to_filter:
        df = df[df[col].notna()]
    return df

def choose_qualified_ones(df):
    import json, ast
    pilot_study_data = pd.read_csv('./pilot_study_data.csv')
    pilot_study_list = []
    for pk, processed_data in zip(pilot_study_data['pk'], pilot_study_data['processed_data']):
        data_dict = ast.literal_eval(processed_data)
        pilot_study_list.append((pk, data_dict))

    for player_data in df['sotopia_pilot_study.1.player.data']:
        actual_dict = ast.literal_eval(player_data)
        for pilot_data in pilot_study_list:
            if pilot_data[-1]['scenario'] == actual_dict['scenario'] and pilot_data[-1]['names'] == tuple(actual_dict['names']):
                player_data_pk = pilot_data[0]
                break
        df['pk'] = player_data_pk
    
    pilot_study_reference = pd.read_csv('./pilot_study_reference.csv')
    pilot_study_reference = pilot_study_reference.to_dict(orient='records')

    player_data = df.to_dict(orient='records')

    comparing_columns = [
        'sotopia_pilot_study.1.player.believability_1',
        'sotopia_pilot_study.1.player.believability_reasoning_1',
        'sotopia_pilot_study.1.player.relationship_1',
        'sotopia_pilot_study.1.player.relationship_reasoning_1',
        'sotopia_pilot_study.1.player.knowledge_1',
        'sotopia_pilot_study.1.player.knowledge_reasoning_1',
        'sotopia_pilot_study.1.player.secret_1',
        'sotopia_pilot_study.1.player.secret_reasoning_1',
        'sotopia_pilot_study.1.player.social_rules_1',
        'sotopia_pilot_study.1.player.social_rules_reasoning_1',
        'sotopia_pilot_study.1.player.financial_and_material_benefits_1',
        'sotopia_pilot_study.1.player.financial_and_material_benefits_reasoning_1',
        'sotopia_pilot_study.1.player.goal_1',
        'sotopia_pilot_study.1.player.goal_reasoning_1',
        'sotopia_pilot_study.1.player.believability_2',
        'sotopia_pilot_study.1.player.believability_reasoning_2',
        'sotopia_pilot_study.1.player.relationship_2',
        'sotopia_pilot_study.1.player.relationship_reasoning_2',
        'sotopia_pilot_study.1.player.knowledge_2',
        'sotopia_pilot_study.1.player.knowledge_reasoning_2',
        'sotopia_pilot_study.1.player.secret_2',
        'sotopia_pilot_study.1.player.secret_reasoning_2',
        'sotopia_pilot_study.1.player.social_rules_2',
        'sotopia_pilot_study.1.player.social_rules_reasoning_2',
        'sotopia_pilot_study.1.player.financial_and_material_benefits_2',
        'sotopia_pilot_study.1.player.financial_and_material_benefits_reasoning_2',
        'sotopia_pilot_study.1.player.goal_2',
        'sotopia_pilot_study.1.player.goal_reasoning_2'
    ]

    qualified_annotators = []
    for data in player_data:
        qualified = True
        prolific_id = data['sotopia_pilot_study.1.player.prolific_id']
        for ref in pilot_study_reference:
            if data['pk'] == ref['PK']:
                for column in comparing_columns:
                    if 'reasoning' not in column and 'goal' in column:
                        ref_column_name = column.split('.')[-1]
                        print(column, ref_column_name)
                        print(data[column], ref[ref_column_name])
                        if abs(data[column] - ref[ref_column_name]) > 2:
                            qualified = False
                            break
            if qualified is False:
                break
        if qualified is True:
            qualified_annotators.append(prolific_id)
    return qualified_annotators


df = pd.read_csv('./all_apps_wide-2024-01-25.csv')
df = filter_out_useless_data(df)
qualified_annotators = choose_qualified_ones(df)

df = df[columns_to_filter]

df.to_csv('./filtered_prolific.csv')

print(qualified_annotators)