from otree.api import *
import os
import json
import re
from collections import defaultdict


def read_json_files():
    directory = './sotopia_survey/GPT4-3.5'

    # List all JSON files in the directory
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

    # Initialize a list to store all JSON data
    all_json_data = []

    # Loop through the JSON files and read their contents
    for file in json_files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            all_json_data.append(data['rewards_prompt'])
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
    # TODO very important, before the secret of the first person, it would have two whitespace
    text = text.replace('  ', ' ') 
    pattern = (
        rf"{name}'s background: {name} is a (\d+)-year-old (.*?)\. (.*?) pronouns\."
        rf"(.*?)\. Personality and values description: (.*?)\. {name.split(' ')[0]}'s secrets: (.*?)(?:\.|\n)"
    )
    #pattern = rf"{name}'s background: {name} is a (\d+)-year-old (.*?)\. (.*?) pronouns\. (.*?)\. Personality and values description: (.*?)\.  {name.split(' ')[0]}'s secrets: (.*?)\n"
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
    import pdb; pdb.set_trace()
    return f"No information found for {name}."


def parse_conversation(convo_text, names):
    # Split the conversation into turns
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
player_annotated_data = defaultdict(list)

for data in raw_dataset:
    names = find_names(data)
    personal_info = {name: parse_personal_info(data, name) for name in names}
    social_goal = {name: parse_social_goal(data, name) for name in names}
    parsed_conversation = parse_conversation(data, names)
    scenario = parse_scenario(data)
    processed_dataset.append({
        'scenario': scenario,
        'names': names,
        'personal_info': personal_info,
        'social_goal': social_goal,
        'parsed_conversation': parsed_conversation,
    })



class C(BaseConstants):
    NAME_IN_URL = 'sotopia_survey'
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

    believability = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='believability (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    believability_reasoning = models.StringField(
        label='Reasoning for believability',
    )
    relationship = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='relationship (-5-5)',
        max=-5,
        min=5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    relationship_reasoning = models.StringField(
        label='Reasoning for relationship',
    )
    knowledge = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='knowledge (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    knowledge_reasoning = models.StringField(
        label='Reasoning for knowledge',
    )
    secret= models.IntegerField(
        widget=widgets.RadioSelect, 
        label='secret (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    secret_reasoning = models.StringField(
        label='Reasoning for secret',
    )
    social_rules = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='social_rules (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    social_rules_reasoning = models.StringField(
        label='Reasoning for social_rules',
    )
    financial_and_material_benefits = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='financial_and_material_benefits (-5-5)',
        max=5,
        min=-5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    financial_and_material_benefits_reasoning = models.StringField(
        label='Reasoning for financial_and_material_benefits',
    )
    goal = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='goal (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    goal_reasoning = models.StringField(
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
        print('var for template')
        print(len(processed_dataset))
        player_data = processed_dataset[-1]
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
        }

    def is_displayed(self):
        import time
        participant = self.participant
        current_time = time.time()
        return current_time < participant.expiry
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            print('timeout before next page')
            print('length for current data: {}'.format(len(processed_dataset)))
            player.add_queue()
            player_annotated_data[player.prolific_id].pop(-1)
            print('length after timeout: {}'.format(len(processed_dataset)))
        else:
            # only successful jumping to the thank you page pop
            print('finish one successfully, still have {}'.format(len(processed_dataset)))
            player_data = processed_dataset.pop(-1)
            player_annotated_data[player.prolific_id].append(player_data)
            print(player_annotated_data)


    form_model = 'player'
    form_fields = [
        'believability', 
        'believability_reasoning',
        'relationship', 
        'relationship_reasoning',
        'knowledge', 
        'knowledge_reasoning', 
        'secret', 
        'secret_reasoning', 
        'social_rules', 
        'social_rules_reasoning', 
        'financial_and_material_benefits', 
        'financial_and_material_benefits_reasoning', 
        'goal',
        'goal_reasoning',
    ]
    timeout_seconds = 600


class SotopiaEvalInstruction(Page):
    form_model = 'player'
    form_fields = ['prolific_id']

    @staticmethod
    def before_next_page(player, timeout_happened):
        import time
        player.participant.expiry = time.time() + 10


page_sequence = [SotopiaEvalInstruction, SotopiaEval]
