import json
from gtts import gTTS


def GenerateQuestionAudio():
    """
    Generate an audio reading the questions and saves them in Assets folder.
    """
    q_file_path = "./Classes/Question/questions.json"
    with open(q_file_path, "r") as f:
        questions = json.load(f)
    tts = gTTS(text=questions[0]["question"], lang="en")
    tts.save("Assets/Q1.mp3")
    tts = gTTS(text=questions[1]["question"], lang="en")
    tts.save("Assets/Q2.mp3")
    tts = gTTS(text=questions[2]["question"], lang="en")
    tts.save("Assets/Q3.mp3")
