from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'survey'
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
    crt_bat = models.IntegerField(
        label='''
        A bat and a ball cost 22 dollars in total.
        The bat costs 20 dollars more than the ball.
        How many dollars does the ball cost?'''
    )
    crt_widget = models.IntegerField(
        label='''
        If it takes 5 machines 5 minutes to make 5 widgets,
        how many minutes would it take 100 machines to make 100 widgets?
        '''
    )
    crt_lake = models.IntegerField(
        label='''
        In a lake, there is a patch of lily pads.
        Every day, the patch doubles in size.
        If it takes 48 days for the patch to cover the entire lake,
        how many days would it take for the patch to cover half of the lake?
        '''
    )


# FUNCTIONS
# PAGES
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender']


class CognitiveReflectionTest(Page):
    form_model = 'player'
    form_fields = ['crt_bat', 'crt_widget', 'crt_lake']


page_sequence = [Demographics, CognitiveReflectionTest]
