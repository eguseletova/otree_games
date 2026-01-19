from otree.api import *
import random


doc = """
email game
"""

# early stages

# what needs to happen here?
# explanation of matrices, possible pay-offs, goal
# decide what state it will be
# participants are grouped here already
# player types are constant but partners are not across rounds
# in which two army generals must decide on a location for a coordinated attack
# if the state is S1, player 1 does not send any messages.
# if the state is S2, player 1 sends a message that is successfully intercepted with probability 0.2. if the message is transmitted,
# player 2 sends a confirmation message of receipt. this message is intercepted with probability 0.2, and so on.
# as soon as a message is intercepted, communication stops, and players are forced to make a choice
# the updating of information stops at first interception or once 3 messages have been transmitted

## 

class C(BaseConstants):
    NAME_IN_URL = 'emailgame'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    PLAYER1_ROLE = "informant"
    PLAYER2_ROLE = "receiver"
    STATES = ["S1", "S2"]
    MESSAGE_STATUS = [[True, "received"], [False, "intercepted"]]
    INTERCEPTION_WEIGHTS = [0.8, 0.2]

class Subsession(BaseSubsession):
  def creating_session(subsession):
    subsession.group_randomly(fixed_id_in_group=True)

class Group(BaseGroup):
    realized_state = models.StringField()
    message1_sent = models.BooleanField(choices=[[True, "Send message"], [False, "Don't send message"]], label="Would you like to send the message?")
    message1_received = models.BooleanField()
    message2_sent = models.BooleanField(choices=[[True, "Send message"], [False, "Don't send message"]], label="Would you like to send the message?")
    message2_received = models.BooleanField()
    message3_sent = models.BooleanField(choices=[[True, "Send message"], [False, "Don't send message"]], label="Would you like to send the message?")
    message3_received = models.BooleanField()

def determine_state(group: Group):
    group.realized_state = random.choices(C.STATES, weights=[0.2, 0.8])[0]
    return group.realized_state 

class Player(BasePlayer):
    location = models.StringField(choices=[[1, "A"], [2, "B"]], widget=widgets.RadioSelectHorizontal)
    confidence = models.IntegerField(min=0, max=100, blank=False, label="How confident are you that you made the optimal choice?")

def intercept_message(group: Group):
    if group.message1_sent == True:
        group.message1_received = random.choices(C.MESSAGE_STATUS, weights=C.INTERCEPTION_WEIGHTS)[0][0]
        return group.message1_received
    elif group.message1_sent == False:
        group.message1_received = 0
        return group.message1_received
    
    if group.message2_sent == True:
        group.message2_received = random.choices(C.MESSAGE_STATUS, weights=C.INTERCEPTION_WEIGHTS)[0][0]
        return group.message2_received
    elif group.message2_sent == False:
        group.message2_received = 0
        return group.message2_received
    
    if group.message3_sent == True:
        group.message3_received = random.choices(C.MESSAGE_STATUS, weights=C.INTERCEPTION_WEIGHTS)[0][0]
        return group.message3_received
    elif group.message3_sent == False:
        group.message3_received = 0
        return group.message3_received


# PAGES
class Hello(Page):
    # explain game play here 

    @staticmethod
    def is_displayed(subsession):
        if subsession.round_number == 1:
            return True

class RoleAnnouncement(Page):
    ## only display this once 
    @staticmethod
    def is_displayed(subsession):
        if subsession.round_number == 1:
            return True

class NewRound(Page):

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        group.realized_state = determine_state(group)


class StateAnnouncement(Page):
    pass
    
class S1Info(Page):
    form_model = "player"
    form_fields = ["location", "certainty"]

    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        if group.realized_state == "S1":
            return True

class S2M1Send(Page):
    form_model = "group"

    @staticmethod
    def get_form_fields(player: Player):
        if player.role == "informant":
            return ["message1_sent"]
        else:
            return False
    
    @staticmethod
    def is_displayed(player: Player):
        if player.role == "informant":
            return True
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        group.message1_received = intercept_message(group)

class S2M1Received(Page):
    form_model = "group"
    form_fields = ["message2_sent"]

    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        if group.message1_received == True:
            return True

class S2M1Intercepted(Page):
    form_model = "player"
    form_fields = ["location", "confidence"]

    @staticmethod
    def is_displayed(group):
        if group.message1_received == False:
            return True 

class Final(Page):
    pass

page_sequence = [Hello, RoleAnnouncement, NewRound, StateAnnouncement, S1Info, S2M1Send, S2M1Received, S2M1Intercepted, Final]
