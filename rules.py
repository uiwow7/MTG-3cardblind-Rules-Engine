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

class Effect:
    def __init__(self, fns, game):
        self.fns = fns 
        self.game = game
        self.players = game.players
    def run(self, event, iss = False):
        for fn in self.fns:
            if len(self.game.stack) == 0 and self.game.phase in Phase.main or not iss:
                fn(self.players, event, iss)
            
class Event:
    def __init__(self, typ, info) -> None:
        self.typ = typ
        self.info = info
        
class Life:
    def __init__(self, a):
        self.a = a
 
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
    def play(self):
        """
        Plays the card.
        """
        if self.zone in self.isCastable and ():
            self.zone = Zone.battlefield