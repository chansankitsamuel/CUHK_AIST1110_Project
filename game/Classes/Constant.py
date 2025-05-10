import pygame


class Constant:
    """
    Hold some game constants that need can be accessed in multiple files
    """

    # window attributes
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    FPS = 60
    # Player's Name
    Player_Name = "You"
    AI_Name = "AI"
    # colours
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    LIGHT_BLUE = (173, 216, 230)
    BLUE = (100, 149, 237)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    # font
    FONT_NAME = pygame.font.match_font("arial")
