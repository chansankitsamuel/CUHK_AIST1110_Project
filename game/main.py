from dotenv import load_dotenv
import os

from Classes.Game import Game
from Classes.Question.GenerateQuestions import GenerateQuestions
from Classes.Question.GenerateQuestionAudio import GenerateQuestionAudio


if __name__ == "__main__":
    # get chatgpt api key
    load_dotenv()
    AZURE_API_KEY = os.getenv("AZURE_API_KEY")
    # generate questions & answerers with chatGPT
    GenerateQuestions(AZURE_API_KEY)
    # generate question audio voice with Google Text-to-speech
    GenerateQuestionAudio()
    game = Game()
    game.run()
