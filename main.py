import rules, presets

class Game:
    def __init__(self, players: list[rules.Player]):
        self.players = players
        self.winner = None
        self.stack = []
    
class Manager:
    def __init__(self, game: Game):
        self.players = game.players
        self.g1 = game
        self.g2 = Game([game.players[1], game.players[0]])
        self.g1.players[0].game = self.g1
        self.g1.players[1].game = self.g1
        self.g2.players[0].game = self.g2
        self.g2.players[1].game = self.g2
        self.result = rules.Result.tie
    def turnCycle(self):
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
        