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
        self.losstie = 0.5
        self.losswin = 1
        self.tiewin= 1.5

class Effect:
    def __init__(self, fns, game):
        self.fns = fns 
        self.game = game
        self.players = game.players
    def run(self, event, iss = False, putOnStack  = True):
        for fn in self.fns:
            if putOnStack:
                if len(self.game.stack) == 0 and self.game.phase in Phase.main or not iss:
                    self.game.stack.append([fn, event])
            else:
                fn(event, self.game)
    def resolve(self, efl: list):
        fn = efl[0]
        event = efl[1]
        fn(event, self.game)
                
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
        
class Tap:
    def __init__(self, creature):
        self.c = creature
    def validate(self, game):
        return not self.c.tapped
    def apply(self, game):
        self.c.tapped = True
 
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
    def __init__(self, game, name: str, cardtypes: list, subtypes: list, abilities: list, cost: list, tags: list = [], pow = None, tou = None, loyalty = None, counters: list = []):
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
        self.tags = tags
        self.misc = {}
        
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
        if self.zone in self.isCastable and (len(self.game.stack) == 0 and self.game.phase in Phase.main or not CardType.land in self.cardtypes) and self.validateCost(False):
            self.zone = Zone.battlefield
            self.validateCost()
            if "etbstapped" in self.tags:
                self.tapped = True
            for ability in self.abilities:
                if type(ability) == Trigger:
                    ability.recieve(Event("etb"))
                    ability.recieve(Event("zonechange", self.zone))
            if CardType.creature in self.cardtypes:
                self.summoningSick = True
    def validateCost(self, payCost = True):
        """
        Checks if a player is able to pay the cost of this card (lands will have no cost, and so this function will always return True for them).
        """
        endr = self.cost
        for m in self.game.players[0].possibleMana:
            try:
                endr.pop(self.cost.index(m.produce))
                if payCost: self.game.players[0].possibleMana.index(m).apply()
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
            if payCost: i.apply(self.game) # make sure the player actually pays the cost
             
        self.game.players[0].update()
        self.game.players[1].update()
        return True
    def untap(self):
        self.tapped = False
        self.game.players[0].update()
        self.game.players[1].update()
    def upkeepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("upkeepstart"))
        self.game.players[0].update()
        self.game.players[1].update()
    def upkeepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("upkeepend"))
        self.game.players[0].update()
        self.game.players[1].update()
    def drawStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("drawstart"))
        self.game.players[0].update()
        self.game.players[1].update()
    def drawEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("drawend"))
        self.game.players[0].update()
        self.game.players[1].update()
    def main1Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main1start"))
        self.game.players[0].update()
        self.game.players[1].update()
    def main1End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main1end"))
        self.game.players[0].update()
        self.game.players[1].update()
    def beginCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("begincombat"))
        self.game.players[0].update()
        self.game.players[1].update()
    def declareAttackers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("declareattackers", self.game.attackers))
        self.game.players[0].update()
        self.game.players[1].update()
    def declareBlockers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("declareblockers", self.game.blockers))
        self.game.players[0].update()
        self.game.players[1].update()
    def endCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("endcombat"))
        self.game.players[0].update()
        self.game.players[1].update()
    def main2Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main2start"))
        self.game.players[0].update()
        self.game.players[1].update()
    def main2End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("main2end"))
        self.game.players[0].update()
        self.game.players[1].update()
    def endStepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("endstepstart"))
        self.game.players[0].update()
        self.game.players[1].update()
    def endStepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("endstepend"))
        self.game.players[0].update()
        self.game.players[1].update()
    def cleanup(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("cleanup"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opupkeepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opupkeepstart"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opupkeepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opupkeepend"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opdrawStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdrawstart"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opdrawEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdrawend"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opmain1Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain1start"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opmain1End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain1end"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opbeginCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opbegincombat"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opdeclareAttackers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdeclareattackers", self.game.attackers))
        self.game.players[0].update()
        self.game.players[1].update()
    def opdeclareBlockers(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opdeclareblockers", self.game.blockers))
        self.game.players[0].update()
        self.game.players[1].update()
    def opendCombat(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opendcombat"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opmain2Start(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain2start"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opmain2End(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opmain2end"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opendStepStart(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opendstepstart"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opendStepEnd(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opendstepend"))
        self.game.players[0].update()
        self.game.players[1].update()
    def opcleanup(self):
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("opcleanup"))
        self.game.players[0].update()
        self.game.players[1].update()
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
        self.game.players[0].update()
        self.game.players[1].update()
    def kill(self):
        self.zone = Zone.graveyard
        for ability in self.abilities:
            if type(ability) == Trigger:
                ability.recieve(Event("die"))
                ability.recieve(Event("zonechange", self.zone))
        self.reset()
        
class Player:
    def __init__(self, deck: list[Card]):
        self.begin = deck
        self.library: list[Card] = []
        self.hand: list[Card] = self.begin
        self.graveyard: list[Card] = []
        self.exile: list[Card] = []
        self.battlefield: list[Card] = []
        self.lands: list[Card] = []
        self.life: int = 20
        self.counters = []
        self.game = None # MUST BE SET LATER
        self.canLoseGame = True
        self.possibleMana = []
        self.instantSpeed = []
        self.creatures = []
        for card in self.begin:
            if "instant-speed" in card.tags:
                self.instantSpeed.append(1)
            else:
                for ability in card.abilities:
                    if type(ability) == ActivatedAbility:
                        if not ability.isSorcery:
                            self.instantSpeed.append(2)
        self.instantSpeed = not len(self.instantSpeed) == 0
                        
    def update(self):
        """
        Checks state-based actions and updates variables. Needs to be called every time the game state is changed.
        """
        for c in self.battlefield:
            if CardType.land in c.cardtypes:
                self.lands.append(c)
                self.possibleMana.append(c.misc["manaProduction"])
            elif CardType.creature in c.cardtypes:
                if c.tou <= 0:
                    c.kill()
                else:
                    self.creatures.append(c)
        poison = 0
        for counter in self.counters:
            if counter.typ == "poison":
                poison += 1
        if self.life <= 0 or poison >= 10:
            self.lose()
            
        if len(self.game.stack) 
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
            self.game.result = Result.loss
                        
class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.winner = None
        self.stack = []
        self.landsPlayedThisTurn = []
        self.possibleMana = []
        self.landsPerTurn = 1
        self.opponent = players[1]
        self.me = players[0]
    def validateCost(self, cost, payCost = True):
        """
        Checks if a player is able to pay a cost for a spell of ability.
        """
        endr = cost
        for m in self.players[0].possibleMana:
            try:
                endr.pop(cost.index(m.produce))
                if payCost: self.players[0].possibleMana.index(m).apply()
            except:
                print("TODO: Extra mana. Relay to decision-maker for optimal play.")
                exit(1)
        if len(endr) == 0:
            return True
        for i in endr:
            if i in Mana.all:
                return False
            else:
                if not i.validate(self): return False # anything in the cost list should have a validate function
        for i in endr:
            if payCost: i.apply(self) # make sure the player actually pays the cost
        return True
    def resolveAll(self):
        for item in self.stack.reverse():
            Effect.resolve(item)
    def resolve(self):
        Effect.resolve(self.stack[-1])