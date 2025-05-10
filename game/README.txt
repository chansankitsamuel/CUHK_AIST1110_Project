1. This project uses the third party, openai, to generate questions & answers
   for each round of the game

2. All external multimedia resources used to create in this project
   are in the Assets folder. Their credits are as follows:

   a. Q1.mp3, Q2.mp3. Q3.mp3:
      Played when a new round of game begins.
      Generated from Google Text-to-speech (gtts) in every run
   b. background.mp3:
      Used as background music for each round of the game
      Sound source: https://www.youtube.com/watch?v=_6WlzEZ95BU
      License: https://creativecommons.org/licenses/by/3.0/legalcode
   c. cymbal.mp3:
      Used as music when a round of game ends
      Sound source: https://www.youtube.com/watch?v=RQmaTF161f8
      License: https://creativecommons.org/licenses/by/3.0/legalcode
   d. correct.mp3:
      Played when any player guesses a correct popular answer
      Sound source: https://www.youtube.com/watch?v=ymtpK5Eg8pQ
      License: https://creativecommons.org/licenses/by/3.0/legalcode
   e. incorrect.mp3:
      Played when the player guesses an incorrect answer
      Sound source: https://www.youtube.com/watch?v=RPidJ39lcLE
      License: https://creativecommons.org/licenses/by/3.0/legalcode
   f. background.png:
      Background of the game
      Source: https://pixabay.com/illustrations/texture-background-graphic-arts-2072344/
      License: https://pixabay.com/service/license-summary/
      (the image was tuned darker)
   g. audience1.png, audience2.png:
      Image of the audience members
      Image source 1: https://openmoji.org/library/emoji-1F9D1-200D-1F9B2/
      Image source 2: https://openmoji.org/library/emoji-1F471-200D-2640-FE0F/
      License: https://creativecommons.org/licenses/by-sa/4.0/
      (as for audience1_green.png, audience1_red.png, audience2_green.png, and
      audience2_red.png, they are edited from the above 2 images by ourselves)

3. Please put the .env file on the root directory, which contains your AZURE_API_KEY

4. The packages requirements are included in requirements_conda.txt and requirements_pip.txt