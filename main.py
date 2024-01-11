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
        self.result = rules.Result.tie
    def turnCycle(self):
        