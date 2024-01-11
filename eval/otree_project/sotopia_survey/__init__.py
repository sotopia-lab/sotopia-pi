from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'sotopia_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(label='What is your age?', min=13, max=125)
    gender = models.StringField(
        choices=[['Male', 'Male'], ['Female', 'Female']],
        label='What is your gender?',
        widget=widgets.RadioSelect,
    )
    crt_agent1 = models.IntegerField(
        widget=widgets.RadioSelect,

    )
    crt_agent2 = models.IntegerField(
        widget=widgets.RadioSelect,
        choices=[-3, -2, -1, 0, 1, 2, 3]
    )


    believability = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='believability (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    relationship = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='relationship (-5-5)',
        max=-5,
        min=5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    knowledge = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='knowledge (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )
    secret= models.IntegerField(
        widget=widgets.RadioSelect, 
        label='secret (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    social_rules = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='social_rules (-10-0)',
        max=0,
        min=-10,
        choices=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    )
    financial_and_material_benefits = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='financial_and_material_benefits (-5-5)',
        max=5,
        min=-5,
        choices=[-5,-4,-3,-2,-1,0,1,2,3,4,5]
    )
    goal = models.IntegerField(
        widget=widgets.RadioSelect, 
        label='goal (0-10)',
        max=10,
        min=0,
        choices=[0,1,2,3,4,5,6,7,8,9,10]
    )




# FUNCTIONS
# PAGES
class SotopiaEval(Page):
    form_model = 'player'
    form_fields = ['believability', 'relationship', 'knowledge', 'secret', 'social_rules', 'financial_and_material_benefits', 'goal']


class SotopiaEvalInstruction(Page):
    form_model = 'player'


page_sequence = [SotopiaEvalInstruction, SotopiaEval]
