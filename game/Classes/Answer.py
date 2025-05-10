class Answer:
    """
    Hold an answer and its corresponding points
    """

    def __init__(self, text: str, points: int):
        self.text: str = text.upper()
        self.points: int = points
        self.is_guessed: bool = False
        self.who_guessed: str = ""

    # call when the answer is guessed
    def guess(self):
        self.is_guessed = True

    # reset the answer
    def reset(self):
        self.is_guessed = False
        self.who_guessed = ""
