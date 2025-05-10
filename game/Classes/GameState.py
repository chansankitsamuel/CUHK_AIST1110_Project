from enum import Enum


class GameState(Enum):
    """
    Hold all gamestates (just for convenience and consistency)
    """

    MENU = 1
    LOADING = 2
    RACE_ACTIVE = 3
    RACE_END = 4
    GAME_OVER = 5
    QUITTING = 6
