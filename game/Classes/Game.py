import pygame
import random
import sys
import json
from dotenv import load_dotenv
import os

from Classes.Constant import Constant
from Classes.GameState import GameState
from Classes.Question.Question import Question
from Classes.Player import Player
from Classes.Audience import Audience
from Classes.UIComponents import InputBox
from Classes.Question.GenerateQuestions import GenerateQuestions
from Classes.Question.GenerateQuestionAudio import GenerateQuestionAudio


# get chatgpt api key
load_dotenv()
AZURE_API_KEY = os.getenv("AZURE_API_KEY")


# AIPlayer is defined here because its method depends on
# the Game & GameState class
class AIPlayer(Player):
    """
    Hold information about the AI player, who guesses an answer irregularly.
    """

    def __init__(self, name: str = "AI"):
        super().__init__(name)
        self.decision_timer = 0
        self.decision_delay = 5  # make initial guess after 5 seconds

    # update ai player to make decisions with random delay
    def update(self, dt: float, game: "Game"):
        if game.game_state != GameState.RACE_ACTIVE:
            # return when the round is ended
            return
        self.decision_timer += dt
        if self.decision_timer >= self.decision_delay:
            self.decision_timer = 0
            # random 3-7 seconds delay after each guess
            self.decision_delay = random.uniform(3, 7)
            self._make_decision(game)

    # make the guess
    def _make_decision(self, game: "Game"):
        current_question = game.get_current_question()
        if not current_question:
            # return when cannot get current question
            return
        unguessed = current_question.get_unguessed_answers()
        if not unguessed:
            # return if no more unguessed answer
            return
        if random.random() < 0.4:  # 40% of the time make correct guess
            chosen_answer = random.choice(unguessed)
            game._check_answer(chosen_answer.text, self)
        else:
            # make incorrect guess
            game._check_answer("INVALID_AI_GUESS", self)


# UIManager is also defined here because its method depends on
# the Game & GameState class
class UIManager:
    """
    Centralized the drawing of user interface.
    """

    def __init__(self, game: "Game"):
        self.game = game

        # font size
        self.font_large = pygame.font.Font(Constant.FONT_NAME, 36)
        self.font_medium = pygame.font.Font(Constant.FONT_NAME, 24)
        self.font_small = pygame.font.Font(Constant.FONT_NAME, 18)

        # input box
        self.input_box_width = 400
        self.input_box_height = 40
        self.input_box_x = (Constant.SCREEN_WIDTH - self.input_box_width) // 2
        self.input_box_y = Constant.SCREEN_HEIGHT - 120
        self.input_box = InputBox(
            self.input_box_x,
            self.input_box_y,
            self.input_box_width,
            self.input_box_height,
            self.font_medium,
        )

        # pop-up message
        self.message = ""
        self.message_timer = 0
        self.message_duration = 2.0

        self.guess_popups = []

    # handle keyboard, mouse events
    def handle_event(self, event: pygame.event.Event | int) -> bool:
        if self.game.game_state == GameState.RACE_ACTIVE:
            if event != 0:
                return self.input_box.handle_event(event)
            else:
                self.input_box.handle_hold_backspace()
        return False  # return false if backspace is pressed

    # udpate messages, popups, input box
    def update(self, dt: float):
        if self.message_timer > 0:
            self.message_timer -= dt
            # empty message if timer reach zero
            if self.message_timer <= 0:
                self.message = ""
        # clear popup from the list when timer reach zero
        for popup in self.guess_popups[:]:
            popup["timer"] -= dt
            if popup["timer"] <= 0:
                self.guess_popups.remove(popup)

        self.input_box.update(dt)  # update input box

    # draw most UI elements in the game
    def draw(self, screen: pygame.Surface):
        # background
        background = pygame.image.load("./Assets/background.png")
        background = pygame.transform.scale(
            background, (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT)
        )
        screen.blit(background, (0, 0))
        # draw UI elements according to the gamestate
        state = self.game.game_state
        if state == GameState.MENU:
            self._draw_menu(screen)
        elif state == GameState.LOADING:
            self._draw_loading(screen)
        elif state == GameState.RACE_ACTIVE or state == GameState.RACE_END:
            self._draw_race(screen)
        elif state == GameState.GAME_OVER:
            self._draw_game_over(screen)
        # draw score
        self._draw_scores(screen)
        # draw messages
        if self.message:
            self._draw_text(
                screen,
                self.message,
                self.font_medium,
                Constant.WHITE,
                Constant.SCREEN_WIDTH // 2,
                Constant.SCREEN_HEIGHT - 30,
                center=True,
            )
        # draw popups
        for popup in self.guess_popups:
            popup_surface = self.font_medium.render(
                popup["text"], True, Constant.WHITE
            )
            # dim the popup gradually
            alpha = int(255 * (popup["timer"] / popup["duration"]))
            popup_surface.set_alpha(alpha)
            text_rect = popup_surface.get_rect(center=popup["pos"])
            screen.blit(popup_surface, text_rect)

    # draw start menu
    def _draw_menu(self, screen: pygame.Surface):
        self._draw_text(
            screen,
            "Race to Score!",
            self.font_large,
            Constant.WHITE,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 3,
            center=True,
        )
        self._draw_text(
            screen,
            "Press SPACE to Start",
            self.font_medium,
            Constant.WHITE,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 2,
            center=True,
        )
        self._draw_text(
            screen,
            "Press ESC to Quit",
            self.font_small,
            Constant.GRAY,
            Constant.SCREEN_WIDTH // 2,
            int(Constant.SCREEN_HEIGHT * 0.7),
            center=True,
        )

    # draw loading screen
    def _draw_loading(self, screen: pygame.Surface):
        self._draw_text(
            screen,
            "Loading...",
            self.font_medium,
            Constant.WHITE,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 2,
            center=True,
        )

    # draw racing screen
    def _draw_race(self, screen: pygame.Surface):
        # draw clock
        self._draw_text(
            screen,
            f"Time Left: {int(self.game.round_time_remaining)}s",
            self.font_medium,
            Constant.WHITE,
            Constant.SCREEN_WIDTH - 200,
            20,
        )
        # draw round
        self._draw_text(
            screen,
            f"Round {self.game.round_number}/{self.game.max_rounds}",
            self.font_small,
            Constant.GRAY,
            10,
            10,
        )

        # draw question
        current_q = self.game.get_current_question()
        if current_q:
            self._draw_text(
                screen,
                current_q.text,
                self.font_medium,
                Constant.WHITE,
                Constant.SCREEN_WIDTH // 2,
                60,
                center=True,
            )
            # draw answer slots
            start_y = 100
            slot_height = 40
            slot_width = 450
            slot_spacing = 8
            for i, answer in enumerate(current_q.answers):
                x_pos = Constant.SCREEN_WIDTH // 2 - slot_width // 2
                y_pos = start_y + i * (slot_height + slot_spacing)
                rect = pygame.Rect(x_pos, y_pos, slot_width, slot_height)
                pygame.draw.rect(screen, Constant.GRAY, rect, 2)
                # guessed answer: in green if guessed by player,
                # guessed answer: in red if gussed by ai
                if answer.is_guessed:
                    self._draw_text(
                        screen,
                        f"{i+1}. {answer.text}",
                        self.font_medium,
                        (
                            Constant.GREEN
                            if answer.who_guessed == Constant.Player_Name
                            else Constant.RED
                        ),
                        x_pos + 15,
                        y_pos + slot_height // 2,
                        center_y=True,
                    )
                    self._draw_text(
                        screen,
                        str(answer.points),
                        self.font_medium,
                        (
                            Constant.GREEN
                            if answer.who_guessed == Constant.Player_Name
                            else Constant.RED
                        ),
                        x_pos + slot_width - 15,
                        y_pos + slot_height // 2,
                        center_y=True,
                        align_right=True,
                    )
                # unguessed answer
                else:
                    # hint first few characters (+1 for every 20 seconds)
                    hint_length = 3 - int(self.game.round_time_remaining) // 20
                    text = "".join(
                        [
                            (
                                f"{letter} "
                                if not letter.isalnum()
                                else (
                                    f"{letter} "
                                    if (
                                        i
                                        < min(
                                            hint_length, len(answer.text) - 1
                                        )
                                    )
                                    else "_ "
                                )
                            )
                            for i, letter in enumerate(answer.text)
                        ]
                    )
                    if self.game.game_state == GameState.RACE_END:
                        text = answer.text
                    self._draw_text(
                        screen,
                        f"{i+1}. {text}",
                        self.font_medium,
                        Constant.GRAY,
                        x_pos + 15,
                        y_pos + slot_height // 2,
                        center_y=True,
                    )

        # draw progress bar (display {player's round score}:{ai's round score})
        bar_width = Constant.SCREEN_WIDTH // 2.5
        bar_height = 20
        bar_x = (Constant.SCREEN_WIDTH - bar_width) // 2
        bar_y = Constant.SCREEN_HEIGHT - 180
        pygame.draw.rect(
            screen, Constant.GRAY, (bar_x, bar_y, bar_width, bar_height), 2
        )
        total = self.game.player1.round_score + self.game.ai_player.round_score
        if total > 0:
            player_ratio = self.game.player1.round_score / total
        else:
            player_ratio = 0.5
        player_bar_width = int(bar_width * player_ratio)
        # player's side in green
        pygame.draw.rect(
            screen,
            Constant.GREEN,
            (bar_x, bar_y, player_bar_width, bar_height),
        )
        # ai's side in red
        pygame.draw.rect(
            screen,
            Constant.RED,
            (
                bar_x + player_bar_width,
                bar_y,
                bar_width - player_bar_width,
                bar_height,
            ),
        )
        # respective scores
        self._draw_text(
            screen,
            f"{self.game.player1.round_score} : "
            f"{self.game.ai_player.round_score}",
            self.font_small,
            Constant.WHITE,
            Constant.SCREEN_WIDTH // 2,
            bar_y + bar_height // 2,
            center=True,
            center_y=True,
        )

        # draw input box and prompts
        if self.game.game_state == GameState.RACE_ACTIVE:
            self.input_box.draw(screen)
            prompt_y = self.input_box.rect.y - 25
            self._draw_text(
                screen,
                "Type your guess and press Enter",
                self.font_small,
                Constant.GRAY,
                Constant.SCREEN_WIDTH // 2,
                prompt_y,
                center=True,
            )
        if self.game.game_state == GameState.RACE_END:
            self._draw_text(
                screen,
                "Time's Up!",
                self.font_large,
                Constant.WHITE,
                Constant.SCREEN_WIDTH // 2,
                Constant.SCREEN_HEIGHT // 2 - 30,
                center=True,
            )
            self._draw_text(
                screen,
                "Press SPACE for Next Round",
                self.font_medium,
                Constant.WHITE,
                Constant.SCREEN_WIDTH // 2,
                Constant.SCREEN_HEIGHT // 2 + 20,
                center=True,
            )

    # draw game over screen
    def _draw_game_over(self, screen: pygame.Surface):
        self._draw_text(
            screen,
            "Game Over!",
            self.font_large,
            Constant.WHITE,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 3,
            center=True,
        )
        winner_text = "It's a tie!"
        if self.game.player1.game_score > self.game.ai_player.game_score:
            winner_text = f"{self.game.player1.name} Win!"
        elif self.game.ai_player.game_score > self.game.player1.game_score:
            winner_text = f"{self.game.ai_player.name} Wins!"
        self._draw_text(
            screen,
            winner_text,
            self.font_medium,
            Constant.WHITE,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 2 - 20,
            center=True,
        )
        self._draw_text(
            screen,
            f"{self.game.player1.name}: {self.game.player1.game_score}",
            self.font_medium,
            Constant.GREEN,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 2 + 30,
            center=True,
        )
        self._draw_text(
            screen,
            f"{self.game.ai_player.name}: {self.game.ai_player.game_score}",
            self.font_medium,
            Constant.RED,
            Constant.SCREEN_WIDTH // 2,
            Constant.SCREEN_HEIGHT // 2 + 60,
            center=True,
        )
        self._draw_text(
            screen,
            "Press SPACE for Menu",
            self.font_small,
            Constant.GRAY,
            Constant.SCREEN_WIDTH // 2,
            int(Constant.SCREEN_HEIGHT * 0.8),
            center=True,
        )

    # helper function: draw scores of both sides
    def _draw_scores(self, screen: pygame.Surface):
        p1_text = (
            f"{self.game.player1.name} | "
            f"Game: {self.game.player1.game_score} | "
            f"Round: {self.game.player1.round_score}"
        )

        ai_text = (
            f"{self.game.ai_player.name} | "
            f"Game: {self.game.ai_player.game_score} | "
            f"Round: {self.game.ai_player.round_score}"
        )
        self._draw_text(
            screen,
            p1_text,
            self.font_medium,
            Constant.GREEN,
            15,
            Constant.SCREEN_HEIGHT - 60,
        )
        self._draw_text(
            screen,
            ai_text,
            self.font_medium,
            Constant.RED,
            Constant.SCREEN_WIDTH - 15,
            Constant.SCREEN_HEIGHT - 60,
            align_right=True,
        )

    # helper function: draw text
    def _draw_text(
        self,
        surface,
        text,
        font,
        color,
        x,
        y,
        center=False,
        center_y=False,
        align_right=False,
    ):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.centerx = x
        elif align_right:
            text_rect.right = x
        else:
            text_rect.left = x
        if center_y:
            text_rect.centery = y
        else:
            text_rect.top = y
        surface.blit(text_surface, text_rect)

    # add messages to be shown on screen
    def show_message(self, text: str, duration: float = 2.0):
        self.message = text
        self.message_timer = duration

    # add popups to be shown on screen
    def add_guess_popup(
        self, text: str, player: Player, duration: float = 2.0
    ):
        if isinstance(player, AIPlayer):
            pos = (Constant.SCREEN_WIDTH - 150, Constant.SCREEN_HEIGHT - 150)
        else:
            pos = (150, Constant.SCREEN_HEIGHT - 150)
        popup = {
            "text": text,
            "pos": pos,
            "timer": duration,
            "duration": duration,
        }
        self.guess_popups.append(popup)


class Game:
    """
    Holding game logic and running game cycle.
    """

    # initialize everything
    def __init__(self):
        # initialize meta-stuffs
        pygame.init()
        pygame.font.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Guess Their Answer")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.frame = 0
        self.running: bool = True
        self.game_state: GameState = GameState.LOADING
        # initialize game variables
        self.questions: list[Question] = []
        self.current_question_index: int = -1
        self.round_number: int = 0
        self.max_rounds: int = 3
        self.round_time_total = 60
        self.round_time_remaining = self.round_time_total
        # initialize classes, elements in the game
        self._load_questions("./Classes/Question/questions.json")
        self.player1: Player = Player(name="You")
        self.ai_player: AIPlayer = AIPlayer(name="AI")
        self.audience: Audience = Audience()
        self.ui_manager: UIManager = UIManager(self)
        self.change_state(GameState.MENU)

    # run the game
    def run(self):
        while self.running:
            dt = self.clock.tick(Constant.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    # handle all mouse, keyboard events in the game
    def _handle_events(self):
        # quit game in quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.change_state(GameState.QUITTING)
                return
            # in start menu
            if self.game_state == GameState.MENU:
                if event.type == pygame.KEYDOWN:
                    # start game when pressing SPACE
                    if event.key == pygame.K_SPACE:
                        self._start_new_game()
                    # quit game when pressing ESC
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.change_state(GameState.QUITTING)
            # in race
            elif self.game_state == GameState.RACE_ACTIVE:
                # handle mouse, keyboard event
                # through (UIManager.handle_event() --> InputBox)
                enter_pressed = self.ui_manager.handle_event(event)
                # submit text in input box if enter is pressed
                if enter_pressed:
                    submitted_text = self.ui_manager.input_box.get_text()
                    # check answer if text is submitted
                    if submitted_text:
                        self._check_answer(submitted_text, self.player1)
                        self.ui_manager.input_box.clear()
            # after race
            elif self.game_state == GameState.RACE_END:
                # press SPACE to start new round or end the game
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                ):
                    if self.round_number >= self.max_rounds:
                        self._end_game()
                    else:
                        self._start_new_round()
            # game over
            elif self.game_state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._generate_new_questions()
                        self.change_state(GameState.MENU)
                        self.player1.reset_game_score()
                        self.ai_player.reset_game_score()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.change_state(GameState.QUITTING)

            # user is resizing window
            if event.type == pygame.VIDEORESIZE:
                old_width = Constant.SCREEN_WIDTH
                old_height = Constant.SCREEN_HEIGHT
                Constant.SCREEN_WIDTH = max(event.w, 600)
                Constant.SCREEN_HEIGHT = max(event.h, 700)
                # adjust audience position accordingly
                self.audience.resize_move(
                    old_width,
                    old_height,
                    Constant.SCREEN_WIDTH,
                    Constant.SCREEN_HEIGHT,
                )
                self.screen: pygame.Surface = pygame.display.set_mode(
                    (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT),
                    pygame.RESIZABLE,
                )

        # additional event handler for holding backspace
        if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
            self.frame += 1
            # send a backspace event every 10 frames to UIManager
            # i.e., delete last character in the input box every 10 frames
            if self.frame >= 10:
                self.frame = 0
                self.ui_manager.handle_event(0)
        else:
            self.frame = 0

    # update everything per dt
    def _update(self, dt: float):
        self.ui_manager.update(dt)  # update UIManager
        # if during race
        if self.game_state == GameState.RACE_ACTIVE:
            self.round_time_remaining -= dt  # update clock
            if self.round_time_remaining <= 0:
                self._end_round()
            self.ai_player.update(dt, self)  # update AIPlayer
            self.audience.update(dt)  # update audience
        # when race ended
        if self.game_state == GameState.RACE_END:
            self.audience.update(dt)  # update audience

    # draw everything on screen
    def _draw(self):
        self.ui_manager.draw(self.screen)
        if (
            self.game_state == GameState.RACE_ACTIVE
            or self.game_state == GameState.RACE_END
        ):
            self.audience.draw(
                self.screen
            )  # draw audience if race is active or just ended

    # load questions from json
    def _load_questions(self, filepath: str):
        self.questions = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for q_data in data:
                    self.questions.append(Question(q_data))
        except Exception as e:
            print(f"An error occurred when loading questions: {e}")

    # start new game if current game ended
    def _start_new_game(self):
        # reset scores
        self.player1.reset_game_score()
        self.ai_player.reset_game_score()
        self.round_number = 0  # reset round
        # reset questions
        self.current_question_index = -1
        for q in self.questions:
            q.reset()
        # start new round
        self._start_new_round()

    # start new round if current round ended
    def _start_new_round(self):
        self.round_number += 1
        # reset scores
        self.player1.reset_round_score()
        self.ai_player.reset_round_score()
        # update question
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            self.current_question_index = 0
            for q in self.questions:
                q.reset()
        current_q = self.get_current_question()
        if current_q:
            current_q.reset()
        # reset audience
        self.audience.reset_positions()
        # reset input box
        self.ui_manager.input_box.clear()
        # reset timer
        self.round_time_remaining = self.round_time_total
        self.ai_player.decision_timer = 0
        # update game state
        self.change_state(GameState.RACE_ACTIVE)
        # show start round message
        self.ui_manager.show_message(f"Round {self.round_number} Start!", 2.0)
        # play the audio of bot reading the current question
        q_recording = pygame.mixer.Sound(f"Assets/Q{self.round_number}.mp3")
        q_recording.play()
        # play background music
        pygame.mixer.music.load("Assets/background.mp3")
        pygame.mixer.music.play(loops=-1)

    # end current round
    def _end_round(self):
        self.change_state(GameState.RACE_END)  # change gamestate
        pygame.mixer.music.stop()  # stop bgm
        # play ending sound effect
        end_sound = pygame.mixer.Sound(f"Assets/cymbal.mp3")
        end_sound.play()

    # check guessed answer
    def _check_answer(self, submitted_text: str, player: Player):
        current_question = self.get_current_question()
        # (just in case)
        if not current_question:
            return
        # special handling for incorrect AI guesses
        if submitted_text == "INVALID_AI_GUESS":
            self.ui_manager.add_guess_popup(
                "AI's Guess is Incorrect!", self.ai_player
            )
            return
        found_answer = current_question.find_answer(
            submitted_text, player.name
        )
        if found_answer:
            if not found_answer.is_guessed:
                # correct and valid guess
                found_answer.guess()
                player.add_score(found_answer.points)
                self.ui_manager.show_message(
                    f"Player: +{found_answer.points} points!", 1.5
                )
                self.ui_manager.add_guess_popup(found_answer.text, player)
                self.audience.react_to_answer(found_answer, player)
                # sound effect for correct guess
                correct_sound = pygame.mixer.Sound(f"Assets/correct.mp3")
                correct_sound.set_volume(0.25)
                correct_sound.play()
                # end the round if all answer is revealed
                if current_question.is_fully_revealed():
                    self.round_time_remaining = 0
            else:
                # correct but invalid guess
                self.ui_manager.add_guess_popup("Already Guessed!", player)
        else:
            # incorrect guess
            self.ui_manager.add_guess_popup("Incorrect Guess!", player)
            # sound effect for incorrect guess
            incorrect_sound = pygame.mixer.Sound(f"Assets/incorrect.mp3")
            incorrect_sound.set_volume(0.25)
            incorrect_sound.play()

    # end the game by changing gamestate to GAME_OVER
    def _end_game(self):
        self.change_state(GameState.GAME_OVER)

    # change the GameState
    def change_state(self, new_state: GameState):
        if self.game_state != new_state:
            self.game_state = new_state
            # deactivate input box if not racing
            if new_state != GameState.RACE_ACTIVE:
                self.ui_manager.input_box.active = False
                self.ui_manager.input_box.color = (
                    self.ui_manager.input_box.color_inactive
                )

    # get the current question by self.current_question_index
    def get_current_question(self) -> Question | None:
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    # generate new question
    def _generate_new_questions(self):
        try:
            GenerateQuestions(AZURE_API_KEY)
            self._load_questions("./Classes/Question/questions.json")
            GenerateQuestionAudio()
        except Exception as e:
            print(f"Failed to generate new questions: {e}")
