from difflib import SequenceMatcher
from Classes.Answer import Answer


# return the similarity score between two strings
def similar(a, b) -> float:
    return SequenceMatcher(None, a, b).ratio()


class Question:
    """
    Hold a question and all the corresponding answers
    """

    # data: dict in the questions.json
    def __init__(self, data: dict):
        self.text: str = data.get("question")
        self.answers: list[Answer] = []
        raw_answers = data.get("answers", [])
        # warp each answer with Answer class
        for ans_data in raw_answers:
            self.answers.append(Answer(ans_data["text"], ans_data["points"]))
        # sort the answers by their point (high to low)
        self.answers.sort(key=lambda x: x.points, reverse=True)

    # get a list of all unguessed answers
    def get_unguessed_answers(self) -> list[Answer]:
        return [ans for ans in self.answers if not ans.is_guessed]

    # find answer according to player's input
    def find_answer(self, text: str, who_guessed) -> Answer | None:
        search_text = text.strip().upper()
        for ans in self.answers:
            # if ans.text == search_text:
            if (
                # just in case some minor typo
                similar(ans.text, search_text)
                > 0.7
            ):
                # record who guessed the answer
                if not ans.is_guessed:
                    ans.who_guessed = who_guessed
                return ans
        return None

    # check if the question is fully revealed
    def is_fully_revealed(self) -> bool:
        return all(ans.is_guessed for ans in self.answers)

    # reset all the answers of the question
    def reset(self):
        for ans in self.answers:
            ans.reset()
