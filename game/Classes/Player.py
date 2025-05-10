class Player:
    """
    Hold a player (should be 1 human player and 1 AI Player)
    Class AIPlayer is defined in game.py for some reason (stated there)
    """

    def __init__(self, name: str = "You"):
        self.name: str = name
        self.round_score: int = 0
        self.game_score: int = 0

    # add points to the player's score count
    def add_score(self, points: int):
        self.round_score += points
        self.game_score += points

    # reset player's round score
    def reset_round_score(self):
        self.round_score = 0

    # reset player's game score
    def reset_game_score(self):
        self.game_score = 0
        self.reset_round_score()
