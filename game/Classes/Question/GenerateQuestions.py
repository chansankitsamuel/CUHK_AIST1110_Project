"""
This program demonstrates how to connect to an Azure OpenAI ChatGPT model.
You need to create a hidden text file, name it as .env, and put it under the
current directory holding this script. Use a text editor to edit the .env file
to add a line AZURE_API_KEY=... where ... is your primary or secondary API key
that you can see in your Profile on the API portal.

Install the required packages in your virtual environment:
pip install dotenv openai
"""

from openai import AzureOpenAI
import json


def GenerateQuestions(AZURE_API_KEY):

    output_path = "./Classes/Question/questions.json"

    # Initialize the client
    client = AzureOpenAI(
        azure_endpoint="https://cuhk-apip.azure-api.net",
        api_version="2024-02-01",  # Use appropriate version for your model
        api_key=AZURE_API_KEY,
    )

    # Chat with gpt-4o-mini or gpt-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    """
Instruction: Create 3 questions, each with 6 most popular answers with
respective scores corresponding to how 'popular' the answer is,
for playing the 'Guess Their Answer' game.

Each answer should not exceed 20 characters, and should not contain
short forms. Convert answers that are direct Cantonese pronunciation
to proper English words where appropriate.
(For example, convert "BOLO BAO" to "PINEAPPLE BUN".)

The points for all 6 answers should sum to 100.
The point allocations to different questions should be different.

Context: The player of this game is Hong Kong people.
The questions and answers should be related to Hong Kong culture.

Please output in json format, below is an example.
Try not to directly copy this example in your output.
```
[
    {
        "question": "Name a popular street food in Hong Kong.",
        "answers": [
            {"text": "EGG WAFFLE", "points": 30},
            {"text": "FISH BALL", "points": 25},
            {"text": "SIU MAI", "points": 18},
            {"text": "EGG TART", "points": 15},
            {"text": "STINKY TOFU", "points": 7},
            {"text": "CHESTNUT", "points": 5}
        ]
    }
]
```
                    """
                ),
            },
        ],
        temperature=0.7,  # Control response creativity (0-1)
    )

    ai_response = response.choices[0].message.content
    output_text = ai_response.split("```")[1].replace("json", "").strip()
    output_json = json.loads(output_text)

    # Dumping the text variable to a JSON file
    with open(output_path, "w") as json_file:
        # noinspection PyTypeChecker
        json.dump(output_json, json_file, indent=4)
