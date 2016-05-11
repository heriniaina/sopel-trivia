# sopel-trivia
Sopel module to have a quizz in your channel

## Installation
* Install sopel from sopel repository
* Change your default.cfg file and add sopel-trivia directory to [extra]
* Copy config.dist.py into config.py and modify it according to your needs
* Fill the table __lalao__ with your questions
    * Note that the database contains also a statistics (see To do list)
* Few malagasy words you may need to know
    * fanontaniana: Question
    * valiny: Answer
    * haavo: Level
    * sokajy: Category


## Commandes
__!lalao__: Start the game
__!top__: Hit

## To do list
* Separate database for quizz and stats