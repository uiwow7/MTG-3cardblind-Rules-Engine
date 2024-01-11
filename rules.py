from dataclasses import dataclass
from enum import auto

@dataclass
class Mana:
    def __init__(self):
        self.W = auto()
        self.U = auto()
        self.B = auto()
        self.R = auto()
        self.G = auto()
        self.C = auto()
        self.X = auto()
        self.A = auto()
        self.white = self.W 
        self.blue = self.U 
        self.black = self.B 
        self.red = self.R 
        self.green = self.G 
        self.colorless = self.C
        self.any = self.A
        self.generic = self.A
        self.all = [self.W, self.U, self.B, self.R, self.G, self.C, self.X, self.A]
        
    
@dataclass
class CardType:
    def __init__(self):
        self.creature = auto()
        self.artifact = auto()
        self.enchantment = auto()
        self.instant = auto()
        self.sorcery = auto()
        self.battle = auto()
        self.planeswalker = auto()
        self.tribal = auto()
        self.land = auto()

@dataclass
class Zone:
    def __init__(self):
        self.hand = auto()
        self.graveyard = auto()
        self.battlefield = auto()
        self.exile = auto()
        self.stack = auto()
        self.library = auto()
        self.deck = self.library
        
@dataclass
class Phase:
    def __init__(self):
        self.begin = auto()
        self.main1 = auto()
        self.combat = auto()
        self.main2 = auto()
        self.end = auto()
        self.main = [self.main1, self.main2]
        
@dataclass
class Result:
    def __init__(self):
        self.win = 2
        self.tie = 1
        self.loss = 0
        self.tieloss = 0.5
        self.winloss = 1
        self.wintie = 1.5

class Effect:
    def __init__(self, fns, game):
        self.fns = fns 
        self.game = game
        self.players = game.players
    def run(self, event, iss = False):
        for fn in self.fns:
            if len(self.game.stack) == 0 and self.game.phase in Phase.main or not iss:
                self.game.stack.append([fn, event, iss])
            
class Event:
    def __init__(self, typ, info = None) -> None:
        self.typ = typ
        self.info = info
        
class Life:
    def __init__(self, a):
        self.a = a
    def validate(self, game):
        return game.players[0].life >= self.a
    def apply(self, game):
        game.players[0].life -= self.a
 
class ActivatedAbility:
    def __init__(self, cost, effect, isSorcery = False):
        self.cost = cost
        self.effect = effect
        self.isSorcery = isSorcery
    def activate(self):
        for e in self.effect:
            e.run(Event("activation"), self.isSorcery)

class Trigger:
    def __init__(self, event, effect):
        self.event = event
        self.effect = effect
    def recieve(self, event):
        if event.typ == self.event.typ:
            for e in self.effect:
                e.run(event)
       
class Card:
    def __init__(self, game, name: str, cardtypes: list, subtypes: list, abilities: list, cost: list, pow = None, tou = None, loyalty = None, counters: list = []):
        self.name = name
        self.cardtypes = cardtypes
        self.subtypes = subtypes
        self.abilities = abilities
        self.cost = cost
        self.pow = pow
        self.tou = tou
        self.loyalty = loyalty
        self.counters = counters
        self.zone = Zone.hand
        self.isCastable = [Zone.hand]
        self.game = game
        self.summoningSick = False
        self.tapped = False
        self.game = game
        
        self.ogmisc = {}
        self.ogname = name
        self.ogcardtypes = cardtypes
        self.ogsubtypes = subtypes
        self.ogabilities = abilities
        self.ogcost = cost
        self.ogpow = pow
        self.ogtou = tou
        self.ogloyalty = loyalty
        self.ogcounters = counters
        self.ogzone = Zone.hand
        self.ogisCastable = [Zone.hand]
        self.oggame = game
        self.ogsummoningSick = False
        self.ogtapped = False
        self.ogmisc = {}
    def play(self):
        """
        Plays the card. Validates cost on its own.
        """
        if self.zone in self.isCastable and (len(self.game.stack) == 0 and self.game.phase in Phase.main or not CardType.land in self.cardtypes) and self.validateCost():
            self.zone = Zone.battlefield
            for ability in self.abilities:
                if type(ability) == Trigger:
                    ability.recieve(Event("etb"))
                    ability.recieve(Event("zonechange", self.zone))
            if CardType.creature in self.cardtypes:
                self.summoningSick = True
    def validateCost(self):
        """
        Checks if the player is able to pay a cost.
        """
        endr = self.cost
        for m in self.game.players[0].possibleMana:
            try:
                endr.pop(self.cost.index(m.produce))
                self.game.players[0].possibleMana.index(m).tapped = True
            except:
                print("TODO: Extra mana. Relay to decision-maker for optimal play.")
                exit(1)
        if len(endr) == 0:
            return True
        for i in endr:
            if i in Mana.all:
                return False
            else:
                if not i.validate(self.game): return False # anything in the cost list should have a validate function
        for i in endr:
            i.apply(self.game) # make sure the player actually pays the cost
        return True
    def untap(self):
        self.tapped = False
    def upkeepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("upkeepstart"))
    def upkeepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("upkeepend"))
    def drawStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("drawstart"))
    def drawEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("drawend"))
    def main1Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main1start"))
    def main1End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main1end"))
    def beginCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("begincombat"))
    def declareAttackers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("declareattackers", self.game.attackers))
    def declareBlockers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("declareblockers", self.game.blockers))
    def endCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("endcombat"))
    def main2Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main2start"))
    def main2End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main2end"))
    def endStepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("endstepstart"))
    def endStepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("endstepend"))
    def cleanup(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("cleanup"))
    def opupkeepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opupkeepstart"))
    def opupkeepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opupkeepend"))
    def opdrawStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdrawstart"))
    def opdrawEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdrawend"))
    def opmain1Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain1start"))
    def opmain1End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain1end"))
    def opbeginCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opbegincombat"))
    def opdeclareAttackers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdeclareattackers", self.game.attackers))
    def opdeclareBlockers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdeclareblockers", self.game.blockers))
    def opendCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opendcombat"))
    def opmain2Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain2start"))
    def opmain2End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain2end"))
    def opendStepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opendstepstart"))
    def opendStepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opendstepend"))
    def opcleanup(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opcleanup"))
    def reset(self):
        self.cardtypes = self.ogcardtypes.copy()
        self.subtypes = self.ogsubtypes.copy()
        self.abilities = self.ogabilities.copy()
        self.cost = self.ogcost.copy()
        self.pow = self.ogpow.copy()
        self.tou = self.ogtou.copy()
        self.loyalty = self.ogloyalty.copy()
        self.counters = self.ogcounters.copy()
        self.zone = self.ogzone.copy()
        self.isCastable = self.ogisCastable.copy()
        self.game = self.oggame.copy()
        self.summoningSick = self.ogsummoningSick.copy()
        self.tapped = self.ogtapped.copy()
        self.misc = self.ogmisc.copy()
    def kill(self):
        self.zone = Zone.graveyard
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("die"))
                ability.recieve(Event("zonechange", self.zone))
        self.reset()
class Player:
    def __init__(self, deck: list[Card]):
        self.library: list[Card] = []
        self.hand: list[Card] = deck
        self.graveyard: list[Card] = []
        self.exile: list[Card] = []
        self.battlefield: list[Card] = []
        self.lands: list[Card] = []
        self.life: int = 20
        self.counters = []
        self.game = None # MUST BE SET LATER
        self.canLoseGame = True
    def update(self):
        """
        Checks state-based actions and updates variables. Needs to be called every time the game state is changed.
        """
        for c in self.battlefield:
            if CardType.land in c.cardtypes:
                self.lands.append(c)
            elif CardType.creature in c.cardtypes:
                if c.tou <= 0:
                    c.kill()
        poison = 0
        for counter in self.counters:
            if counter.typ == "poison":
                poison += 1
        if self.life <= 0 or poison >= 10:
            self.lose()
    def draw(self):
        if len(self.deck) > 0:
            self.hand.append(self.deck.pop())
            for c in self.battlefield:
                for ability in c.abilities:
                    if type(ability) == Trigger:
                        ability.recieve(Event("draw"))
                        
    def lose(self):
        """
        Loses the game. Sends out trigger message, then checks life total and canLoseGame. If both of those are correct, it sends the loss message to the game.
        """
        for c in self.battlefield:
            for ability in c.abilities:
                if type(ability) == Trigger:
                    ability.recieve(Event("lose"))
                    
        if self.life <= 0 and self.canLoseGame:
            self.game.winner = self.game.players[1]