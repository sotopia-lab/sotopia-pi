from otree.api import *
import os
import json
import re
import random
from collections import defaultdict

def read_json_files():
    directory = './sotopia_pilot_study/pilot_study'

    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    all_json_data = []

    for file in json_files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            all_json_data.append((data['pk'], data['rewards_prompt']))
    return all_json_data


def find_names(convo_text):
    match = re.search(r'Participants: ([A-Z][a-z]+ [A-Z][a-z]+) and ([A-Z][a-z]+ [A-Z][a-z]+)', convo_text)
    return (match.group(1), match.group(2)) if match else (None, None)


def parse_scenario(text):
    pattern = r"Scenario: (.*?)\n"
    scenario_match = re.search(pattern, text, re.DOTALL)
    scenario = scenario_match.group(1).strip() if scenario_match else "No scenario found."
    return scenario


def parse_social_goal(text, name):
    goal_pattern = rf"{name}'s goal: (.*?)\n"
    goal_match = re.search(goal_pattern, text, re.DOTALL)
    goal = goal_match.group(1).strip() if goal_match else f"No goal found for {name}."
    return goal


def parse_personal_info(text, name):
    if not name:
        raise Exception("name field is None")
    
    # TODO very important
    # before the secret of the first person
    # it would have two whitespace
    text = text.replace('  ', ' ')
    pattern = (
        rf"{name}'s background: {name} is a (\d+)-year-old (.*?)\. (.*?) pronouns\."
        rf"(.*?)\. Personality and values description: (.*?)\. {name.split(' ')[0]}'s secrets: (.*?)(?:\.|\n)"
    )
    match = re.search(pattern, text, re.DOTALL)
    if match:
        age, profession, pronouns, interests, personality, secrets = match.groups()
        return {
            "name": name,
            "age": age,
            "profession": profession.strip(),
            "pronouns": pronouns.strip(),
            "interests": interests.strip(),
            "personality": personality.strip(),
            "secrets": secrets.strip()
        }
    raise Exception(f"No information found for {name}.")


def parse_conversation(convo_text, names):
    # Split the conversation into turns
    convo_text = convo_text.replace('left the conversation,', 'left the conversation.')
    turns = re.split(r'Turn #\d+\n', convo_text)
    parsed_conversation = []

    for turn in turns:
        # Extract speaker and their dialogue
        for name in names:
            if name in turn:
                dialogue = turn.split(':', 1)[1].strip() if ':' in turn else turn
                parsed_conversation.append({"speaker": name, "dialogue": dialogue})
                break
    return parsed_conversation[1:]


raw_dataset = read_json_files()
processed_dataset = []
pks = []

for data in raw_dataset:
    try:
        pk = data[0]
        rewards_prompt = data[1]
        names = find_names(rewards_prompt)
        personal_info = {name: parse_personal_info(rewards_prompt, name) for name in names}
        social_goal = {name: parse_social_goal(rewards_prompt, name) for name in names}
        parsed_conversation = parse_conversation(rewards_prompt, names)
        scenario = parse_scenario(rewards_prompt)
        processed_data = {
            'scenario': scenario,
            'names': names,
            'personal_info': personal_info,
            'social_goal': social_goal,
            'parsed_conversation': parsed_conversation,
        }
        # TODO (haofeiyu): need to add pk into the player data
        processed_dataset.append(processed_data)
        pks.append(pk)
    except Exception as e:
        print(e, f"; pk: {data[0]}")

import pandas as pd
pd_data = {
    'pk': pks,
    'processed_data': processed_dataset
}
df = pd.DataFrame(pd_data)
df.to_csv('../pilot_study_data.csv')
import pdb; pdb.set_trace()

class C(BaseConstants):
    NAME_IN_URL = 'sotopia_pilot_study'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        self.session.vars['conversation'] = ['hello', 'world', 'darling']

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def add_queue(self):
        data = json.loads(self.data)
        processed_dataset.insert(0, data)

    prolific_id = models.StringField(
        label='Prolific ID',
    )
    believability_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='believability (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    believability_reasoning_1 = models.LongStringField(
        label='Reasoning for believability',
    )
    relationship_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='relationship (-5-5)',
        max=-5,
        min=5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    relationship_reasoning_1 = models.LongStringField(
        label='Reasoning for relationship',
    )
    knowledge_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='knowledge (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    knowledge_reasoning_1 = models.LongStringField(
        label='Reasoning for knowledge',
    )
    secret_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='secret (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    secret_reasoning_1 = models.LongStringField(
        label='Reasoning for secret',
    )
    social_rules_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='social_rules (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    social_rules_reasoning_1 = models.LongStringField(
        label='Reasoning for social_rules',
    )
    financial_and_material_benefits_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='financial_and_material_benefits (-5-5)',
        max=5,
        min=-5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    financial_and_material_benefits_reasoning_1 = models.LongStringField(
        label='Reasoning for financial_and_material_benefits',
    )
    goal_1 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='goal (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    goal_reasoning_1 = models.LongStringField(
        label='Reasoning for goal',
    )

    believability_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='believability (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    believability_reasoning_2 = models.LongStringField(
        label='Reasoning for believability',
    )
    relationship_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='relationship (-5-5)',
        max=-5,
        min=5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    relationship_reasoning_2 = models.LongStringField(
        label='Reasoning for relationship',
    )
    knowledge_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='knowledge (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    knowledge_reasoning_2 = models.LongStringField(
        label='Reasoning for knowledge',
    )
    secret_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='secret (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    secret_reasoning_2 = models.LongStringField(
        label='Reasoning for secret',
    )
    social_rules_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='social_rules (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    social_rules_reasoning_2 = models.LongStringField(
        label='Reasoning for social_rules',
    )
    financial_and_material_benefits_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='financial_and_material_benefits (-5-5)',
        max=5,
        min=-5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    financial_and_material_benefits_reasoning_2 = models.LongStringField(
        label='Reasoning for financial_and_material_benefits',
    )
    goal_2 = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='goal (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    goal_reasoning_2 = models.LongStringField(
        label='Reasoning for goal',
    )
    data = models.LongStringField() 


# FUNCTIONS
# PAGES
class SotopiaEval(Page):
    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1

    @staticmethod
    def vars_for_template(player):
        print(len(processed_dataset))
        player_data = random.choice(processed_dataset)
        player.data = json.dumps(player_data)
        print(len(processed_dataset))
        data = json.loads(player.data)
        for d in data['parsed_conversation']:
            if '\"' in d['dialogue']:
                d['turn'] = f"{d['speaker']} said: {d['dialogue']}"
            else:
                d['turn'] = d['dialogue']

        turn_list = zip(
            [i+1 for i in range(len(data['parsed_conversation']))],
            [d['turn'] for d in data['parsed_conversation']], 
        )
        scenario = data['scenario']
        names = data['names']
        personal_info_1 = data['personal_info'][names[0]]
        social_goal_1 = data['social_goal'][names[0]]
        personal_info_2 = data['personal_info'][names[1]]
        social_goal_2 = data['social_goal'][names[1]]
        return {
            'scenario': scenario,
            'turn_list': turn_list, # 'string_list' is the key for the list of strings
            'personal_info_1': personal_info_1,
            'personal_info_2': personal_info_2,
            'social_goal_1': social_goal_1,
            'social_goal_2': social_goal_2,
            'timer1_duration': 400,
            'timer2_duration': 600,
        }

    def is_displayed(self):
        import time
        participant = self.participant
        current_time = time.time()
        return current_time < participant.expiry

    form_model = 'player'
    form_fields = [
        'believability_1', 
        'believability_reasoning_1',
        'relationship_1', 
        'relationship_reasoning_1',
        'knowledge_1', 
        'knowledge_reasoning_1', 
        'secret_1', 
        'secret_reasoning_1', 
        'social_rules_1', 
        'social_rules_reasoning_1', 
        'financial_and_material_benefits_1', 
        'financial_and_material_benefits_reasoning_1', 
        'goal_1',
        'goal_reasoning_1',
        'believability_2', 
        'believability_reasoning_2',
        'relationship_2', 
        'relationship_reasoning_2',
        'knowledge_2', 
        'knowledge_reasoning_2', 
        'secret_2', 
        'secret_reasoning_2', 
        'social_rules_2', 
        'social_rules_reasoning_2', 
        'financial_and_material_benefits_2', 
        'financial_and_material_benefits_reasoning_2', 
        'goal_2',
        'goal_reasoning_2',
    ]
    timeout_seconds = 1200


class SotopiaEvalInstruction(Page):
    form_model = 'player'
    form_fields = ['prolific_id']

    @staticmethod
    def before_next_page(player, timeout_happened):
        import time
        player.participant.expiry = time.time() + 10


page_sequence = [SotopiaEvalInstruction, SotopiaEval]