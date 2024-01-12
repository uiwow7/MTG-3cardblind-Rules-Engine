import rules, presets, copy
    
class Manager:
    def __init__(self, game: rules.Game):
        self.players = game.players
        self.g1 = game
        self.g2 = rules.Game([game.players[1], game.players[0]])
        self.g1.players[0].game = self.g1
        self.g1.players[1].game = self.g1
        self.g2.players[0].game = self.g2
        self.g2.players[1].game = self.g2
        self.players = self.g1.players
        self.result = rules.Result.tie
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
    def optimalSpellPlaySorcerySpeed(self, game: rules.Game, spells: list[rules.Card]):
        nspells = []
        ldgs = 0
        hds = 0
        for spell in spells:
            if not game.validateCost(spell.cost):
                if "disruption-hand" in spell.tags:
                    nspells.insert(ldgs, spell)
                    hds += 1
                if "disruption-land" in spell.tags:
                    if len(game.players[1].lands) <= 0:
                        nspells.append(spell)
                    else:
                        nspells .insert(0, spell)
                        ldgs += 1
                if ""
    def turnCycle(self):
        self.g1.landsPlayedThisTurn = []
        self.g2.landsPlayedThisTurn = []
        # UNTAP STEP
        for card in self.g1.players[0].begin:
            card.untap()
        for card in self.g2.players[0].begin:
            card.untap()
        # UPKEEP STEP
        for card in self.g1.players[0].begin:
            card.upkeepStart()
        for card in self.g2.players[0].begin:
            card.opupkeepStart()
        for card in self.g1.players[0].begin:
            card.upkeepEnd()
        for card in self.g2.players[0].begin:
            card.opupkeepEnd()
        # DRAW STEP
        for card in self.g1.players[0].begin:
            card.drawStart()
        for card in self.g2.players[0].begin:
            card.opdrawStart()
        for card in self.g1.players[0].begin:
            card.drawEnd()
        for card in self.g2.players[0].begin:
            card.opdrawEnd()
        # MAIN PHASE
        # LAND DROP
        possibleLands = []
        for card in self.players[0].begin:
            if rules.CardType.land in card.cardtypes:
                if card.zone in card.isCastable:
                    possibleLands.append(card)
        self.optimalLandPlay(possibleLands)[0].play()
        
        # PLAY SPELL (No instant speed)
        if not self.players[0].instantSpeed:
            possibleCards = []
            for card in self.players[0].begin:
                if not rules.CardType.land in card.cardtypes:
                    if card.zone in card.isCastable:
                        possibleCards.append(possibleCards)
            self.optimalSpellPlaySorcerySpeed(self.g1, possibleCards)[0].play()