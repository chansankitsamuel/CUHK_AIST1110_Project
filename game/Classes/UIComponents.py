import pygame
from Classes.Constant import Constant


class InputBox:
    """
    Hold the input box, for player to input text
    """

    def __init__(self, x, y, width, height, font, text=""):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True  # active: player can input text; inactive: cannot
        self.color_inactive = Constant.LIGHT_BLUE
        self.color_active = Constant.BLUE
        self.color = self.color_inactive  # default color is inactive color
        self.text = text
        self.font = font
        # the inputted text is displayed on the input box
        self.txt_surface = self.font.render(text, True, self.color)
        # a cursor is also added to indicate the input box is active
        # [ just my OCD Σ(ﾟωﾟ) ]
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.cursor_interval = 0.5  # the cursor blink for each 0.5 second

    # event handler for the input box
    def handle_event(self, event: pygame.event.Event) -> bool:
        self.active = True
        returned_enter = False
        # mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # if player clicked the input box
            if self.rect.collidepoint(event.pos):
                # activate the input box
                self.active = True
                self.color = self.color_active
                self.cursor_visible = True
                self.cursor_timer = 0
            # if player clicked outside the input box
            else:
                # deactivate the input box
                self.active = False
                self.color = self.color_inactive
                self.cursor_visible = False
        # keyboard events
        returned_enter = False
        if event.type == pygame.KEYDOWN:
            # check if the input box is actived
            if self.active:
                # if player hitted return
                if event.key == pygame.K_RETURN:
                    # set the flag to True
                    returned_enter = True
                # if player hitted backspace
                elif event.key == pygame.K_BACKSPACE:
                    # delete the last character in the string
                    self.text = self.text[:-1]

                else:
                    # if player is not hitting some command keybinds,
                    # but characters that can be printed
                    if event.unicode.isprintable():
                        self.text += event.unicode

                # render the inputted text
                self.txt_surface = self.font.render(
                    self.text, True, Constant.WHITE
                )
                # reset cursor timer
                self.cursor_timer = 0

        return returned_enter  # return (if enter is pressed)

    # deal with backspacing answer if exists
    def handle_hold_backspace(self):
        if self.active:
            if len(self.text) >= 1:
                self.text = self.text[:-1]  # delete last character
        # render text
        self.txt_surface = self.font.render(self.text, True, Constant.WHITE)
        # reset cursor
        self.cursor_timer = 0
        self.cursor_visible = True

    # update the cursor in the input box (to achieve blinking cursor)
    def update(self, dt):
        # if the input box is activated
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_interval:
                # toggle the cusor visibility for each cursor_interval
                self.cursor_timer %= self.cursor_interval
                self.cursor_visible = not self.cursor_visible

    # return string from input box
    def get_text(self) -> str:
        return self.text.strip()

    # clear string in the input box
    def clear(self):
        self.text = ""
        # render the empty string
        self.txt_surface = self.font.render(self.text, True, Constant.WHITE)

    # draw the input box on the screen
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, Constant.BLACK, self.rect)  # background
        x_pos = (Constant.SCREEN_WIDTH - self.width) // 2
        y_pos = Constant.SCREEN_HEIGHT - 120
        self.rect = pygame.Rect(x_pos, y_pos, self.width, self.height)
        pygame.draw.rect(screen, self.color, self.rect, 2)  # border
        # vertical position for the text
        text_y = (
            self.rect.y
            + (self.rect.height - self.txt_surface.get_height()) // 2
        )
        # render text surface
        screen.blit(self.txt_surface, (self.rect.x + 5, text_y))
        # check if input box is activated
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + self.txt_surface.get_width()
            # horizontal & vertical position for the cursor
            if cursor_x < self.rect.right - 5:
                cursor_y_start = text_y
                cursor_y_end = text_y + self.txt_surface.get_height()
                # draw cursor
                pygame.draw.line(
                    screen,
                    Constant.WHITE,
                    (cursor_x, cursor_y_start),
                    (cursor_x, cursor_y_end),
                    2,
                )
