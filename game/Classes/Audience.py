import pygame
import random

from Classes.Constant import Constant
from Classes.Answer import Answer
from Classes.Player import Player


class Audience:
    """
    Hold all audience members
    """

    def __init__(self):
        self.members = []
        self.create_audience()

    # create audience members
    def create_audience(self):
        self.members = []
        num_members = 100
        for i in range(num_members):
            # each audience member have random position on the spectator stand
            init_x = Constant.SCREEN_WIDTH / 2 + random.randint(-50, 50)
            init_y = Constant.SCREEN_HEIGHT * 0.7 + random.randint(-50, 50)
            member = self.AudienceMember((init_x, init_y))
            self.members.append(member)

    # update all audience members' position
    def update(self, dt: float):
        for member in self.members:
            member.update(dt)

    # draw all the audience members on screen
    def draw(self, screen: pygame.Surface):
        for member in self.members:
            member.draw(screen)

    # update all audience member's position when the screen resizes
    def resize_move(self, old_width, old_height, new_width, new_height):
        for member in self.members:
            member.resize_move(old_width, old_height, new_width, new_height)

    # audience members react to correct answer
    def react_to_answer(self, answer: Answer, player: Player):
        # if player guessed the answer
        if player.name != Constant.Player_Name:
            # the audience member should go to the left side
            target_x = Constant.SCREEN_WIDTH * 0.8
        # else: AI guessed the answer
        else:
            target_x = Constant.SCREEN_WIDTH * 0.2
        # count the number of audience members leave the spectator stand
        count = 0
        for member in self.members:
            # check if the audience member is still on the spectator stand
            if member.state == "neutral":
                # check the state according to target_x
                member.state = (
                    "left" if target_x < Constant.SCREEN_WIDTH / 2 else "right"
                )  # added some randomness to avoid overlapping
                member.target.x = target_x + random.randint(-50, 50)
                if member.state == "left":
                    member.image = pygame.image.load(
                        f"Assets/audience{member.image_num}_green.png"
                    )
                else:
                    member.image = pygame.image.load(
                        f"Assets/audience{member.image_num}_red.png"
                    )
                member.image = pygame.transform.scale(member.image, (30, 30))
                count += 1
            # break the loop when the number of audience member
            # equals the answer's points
            if count >= answer.points:
                break

    # reset the positions (and states) of all audience members
    def reset_positions(self):
        for member in self.members:
            init_x = Constant.SCREEN_WIDTH / 2 + random.randint(-50, 50)
            init_y = Constant.SCREEN_HEIGHT * 0.62 + random.randint(-50, 50)
            member.pos = pygame.Vector2(init_x, init_y)
            member.target = pygame.Vector2(init_x, init_y)
            member.state = "neutral"
            member.image = pygame.image.load(
                f"Assets/audience{member.image_num}.png"
            )
            member.image = pygame.transform.scale(member.image, (30, 30))

    class AudienceMember:
        """
        Hold each individual audience member, manage their animation
        """

        def __init__(self, pos):
            # use pygame built-in vector to store the position attribute
            self.pos = pygame.Vector2(pos)
            self.target = pygame.Vector2(pos)
            self.speed = 300  # animation speed
            # self.state: "neutral" --> on the spectator stand,
            #              "left" --> on left side, "right" --> on right side
            self.state = "neutral"
            # load the audience image randomly
            if random.random() >= 0.5:
                self.image = pygame.image.load("Assets/audience1.png")
                self.image_num = 1
            else:
                self.image = pygame.image.load("Assets/audience2.png")
                self.image_num = 2
            self.image = pygame.transform.scale(self.image, (30, 30))

        # update the position of the audience member (for the animation)
        def update(self, dt):
            direction = self.target - self.pos
            distance = direction.length()
            if distance > 0:
                move_distance = self.speed * dt
                if move_distance >= distance:
                    self.pos = self.target.copy()  # stop further movement
                else:
                    self.pos += (
                        direction.normalize() * move_distance
                    )  # v.normalize() -> unit vector v

        # draw the audience member on screen (with the correct color)
        def draw(self, screen):
            screen.blit(self.image, (int(self.pos.x), int(self.pos.y)))

        # update audience member's position when the screen resizes
        def resize_move(self, old_width, old_height, new_width, new_height):
            self.speed = 100000
            self.target = pygame.Vector2(
                (
                    self.pos.x / old_width * new_width,
                    self.pos.y / old_height * new_height,
                )
            )
            self.update(1 / Constant.FPS)
            self.speed = 300
