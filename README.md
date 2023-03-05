Snake Game

This is a simple implementation of the classic Snake Game using Python, Flask, HTML, and JavaScript.
Requirements

    python3
    numpy
    flask
    flask_cors
    

How to Run

    Clone the repository to your local machine with 'git clone https://github.com/aauville/snakeGame.git'

    Install the required packages using 'pip install flask numpy flask_cors'

    Run the app.py file using python3 app.py

    Open localhost:5000 in your web browser

How to Play

Use the arrow keys on your keyboard to control the snake. The objective of the game is to eat as many apples as possible without colliding with the walls or your own body. Each time the snake eats an apple, its length increases.

Limits of the Code

    The game currently only has one level and does not have any difficulty settings.

    The game does not have any pause feature.

    The game does not have a score feature.

    The game does not have a 'Game Over' screen

    The game gets stuck in an infinite loop when the snake reaches the maximum size because a new apple can't be generated in the grid


To Improve

    Add different difficulty levels or a progressive difficulty system to make the game more challenging.

    Implement a high score leaderboard to keep track of the top players.

    Implement a pause feature to make the game more user-friendly.