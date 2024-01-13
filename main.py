import rules, presets, copy

    
class Manager:
    def __init__(self, game: rules.Game):
        self.players = game.players
        self.g1 = game
        self.g2 = rules.Game([game.opponent, game.me])
        self.g1.me.game = self.g1
        self.g1.opponent.game = self.g1
        self.g2.me.game = self.g2
        self.g2.opponent.game = self.g2
        self.players = self.g1.players
        self.result = rules.Result.tie
        self.tree = {}
        
    def optimalLandPlay(self, lands: list[rules.Card]) -> list[rules.Card]:
        nlands = []
        taplands = 0
        for i, land in enumerate(lands):
            if "storage" in land.tags:
                nlands.insert(0, land)
            elif "etbstapped" in land.tags:
                nlands.append(land)
                taplands += 1
            else:
                nlands.insert(i - taplands, land)
        return nlands
    
    def turnCycle(self):
        self.g1.landsPlayedThisTurn = []
        self.g2.landsPlayedThisTurn = []
        # UNTAP STEP
        for card in self.g1.me.begin:
            card.untap()
        for card in self.g2.me.begin:
            card.untap()
        # UPKEEP STEP
        for card in self.g1.me.begin:
            card.upkeepStart()
        for card in self.g2.me.begin:
            card.opupkeepStart()
        for card in self.g1.me.begin:
            card.upkeepEnd()
        for card in self.g2.me.begin:
            card.opupkeepEnd()
        # DRAW STEP
        for card in self.g1.me.begin:
            card.drawStart()
        for card in self.g2.me.begin:
            card.opdrawStart()
        for card in self.g1.me.begin:
            card.drawEnd()
        for card in self.g2.me.begin:
            card.opdrawEnd()
        # MAIN PHASE
        # LAND DROP
        possibleLands = []
        for card in self.g1.me.begin:
            if rules.CardType.land in card.cardtypes:
                possibleLands.append(card)
        self.optimalLandPlay(possibleLands)[0].play()
        
        # SORCERY SPEED SPELLS
        self.processSpell()
    
    def processSpell(self):
        # SORCERY SPEED SPELLS
        possibleSpells: list[rules.Card] = []
        for spell in self.g1.me.begin:
            if not rules.CardType.land in spell.cardtypes and self.g1.validateCost(spell.cost, False) and not "instant-speed" in spell.tags and not "wait" in spell.tags:
                possibleSpells.append(spell)
        
        # CREATE DECISION TREES FOR EACH NON-<wait> SPELL
        managers = []
        for spell in possibleSpells:
            game = copy.deepcopy(self.g1)
            spell.play()
            game2 = self.g1
            nmanager = Manager(game2)
            self.g1 = game
            managers.append(nmanager)
        