import numpy as np
from flask import Flask, jsonify, request, render_template, make_response
from flask_cors import CORS

app = Flask(__name__, template_folder='../frontend/')
CORS(app)


# values of the grid
EMPTY = 0
SNAKE = 1
APPLE = 2

# directions
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

directions: dict = {"UP": UP, "DOWN": DOWN, "LEFT": LEFT, "RIGHT": RIGHT}

# default values before initialization
height = 10
width = 10
number_of_apples = 1


def up_neighbor_coordinates(box: "tuple[int, int]"):
    return (box[0] - 1, box[1])


def right_neighbor_coordinates(box: "tuple[int, int]"):
    return (box[0], box[1] + 1)


def down_neighbor_coordinates(box: "tuple[int, int]"):
    return (box[0] + 1, box[1])


def left_neighbor_coordinates(box: "tuple[int, int]"):
    return (box[0], box[1] - 1)


class Snake:
    def __init__(self):
        self.game_grid = np.zeros((height, width))

        snake_init_head = (
            np.random.randint(1, height - 1),
            np.random.randint(1, width - 1),
        )  # init snake head far from edge to avoid spawnkill

        self.snake_body_coordinates: "list[tuple[int, int]]" = [snake_init_head]
        self.game_grid[snake_init_head[0], snake_init_head[1]] = SNAKE

        for _ in range(number_of_apples):
            apple_coordinates: "tuple[int, int]" = snake_init_head
            while (
                apple_coordinates == snake_init_head
                or self.game_grid[apple_coordinates[0], apple_coordinates[1]] == APPLE
            ):
                apple_coordinates = (
                    np.random.randint(height),
                    np.random.randint(width),
                )
            self.game_grid[apple_coordinates[0], apple_coordinates[1]] = APPLE

        self.win_status: int = 0  # 0 if game currently running, 1 if game won
        self.lost_status: int = 0  # 0 if game currently running, 1 if game lost
        self.direction: int = UP  # initial direction

    # functions used to return the coordinates of the neighbors

    def get_snake_head_coordinates(self):
        return self.snake_body_coordinates[0]

    def get_snake_tail_coordinates(self):
        return self.snake_body_coordinates[-1]

    def is_apple(self, box: "tuple[int, int]"):
        return self.game_grid[box[0], box[1]] == APPLE

    def add_random_apple(self):
        new_apple_coordinates = (np.random.randint(height), np.random.randint(width))
        while (
            self.game_grid[new_apple_coordinates[0], new_apple_coordinates[1]] != EMPTY
        ):
            new_apple_coordinates = (
                np.random.randint(height),
                np.random.randint(width),
            )
        self.game_grid[new_apple_coordinates[0], new_apple_coordinates[1]] = APPLE

    def update_snake(self, new_box):
        """
        Moves the snake towards the new_box.
        Grows the snake if new_box is an apple.

        Args:
            new_box (tuple[int, int]): coordinates of the box the snake is heading to
        """
        self.snake_body_coordinates.insert(0, new_box)
        if self.is_apple(new_box):
            self.game_grid[new_box[0], new_box[1]] = SNAKE
            self.add_random_apple()
        else:
            self.game_grid[new_box[0], new_box[1]] = SNAKE
            tail: "tuple[int, int]" = self.get_snake_tail_coordinates()
            self.game_grid[tail[0], tail[1]] = EMPTY
            self.snake_body_coordinates.pop()

    def is_accessible(self, new_box):
        is_box_out_of_range: bool = (
            new_box[0] < 0
            or new_box[0] >= height
            or new_box[1] < 0
            or new_box[1] >= width
        )
        if is_box_out_of_range:
            return False
        is_box_snake: bool = self.game_grid[new_box[0], new_box[1]] == SNAKE
        if is_box_snake:
            return False
        return True

    def update_grid(self):
        """
        if the game is not won or lost, updates the grid according to the direction of the snake
        if the new box is not accessible, the game is lost
        if the snake has reached the maximum length, the game is won

        Raises:
            Exception: raises an exception if the direction is invalid

        Returns:
            Response : returns the updated grid in a json format
        """
        if self.win_status == 0 and self.lost_status == 0:
            snake_head_coordinates = self.get_snake_head_coordinates()
            if self.direction == UP:
                new_box_coordinates = up_neighbor_coordinates(snake_head_coordinates)
            elif self.direction == RIGHT:
                new_box_coordinates = right_neighbor_coordinates(snake_head_coordinates)
            elif self.direction == DOWN:
                new_box_coordinates = down_neighbor_coordinates(snake_head_coordinates)
            elif self.direction == LEFT:
                new_box_coordinates = left_neighbor_coordinates(snake_head_coordinates)
            else:
                raise Exception("Invalid direction")

            if self.is_accessible(new_box_coordinates):
                self.update_snake(new_box_coordinates)
            elif len(self.snake_body_coordinates) == height * width:
                self.win_status = 1
            else:
                self.lost_status = 1
        game_grid_list = (
            self.game_grid.tolist()
        )  # conversion to python list for easier managing of information
        return jsonify(game_grid_list)  # conversion to json file for the xhr request

    def update_direction(self):
        direction_response = request.form["direction"]
        self.direction = directions[direction_response]
        return "Direction updated to " + direction_response

    def send_winning_status(self):
        return jsonify([self.win_status, self.lost_status])


@app.route("/size", methods=["POST"])
def update_size():
    """
    Updates the size of the grid and the number of apples if the input is valid
    
    Returns:
        string: returns a string to confirm the update
    """
    global height, width, number_of_apples
    local_height = int(request.form["height"])
    if local_height > 0:
        height = local_height
    local_width = int(request.form["width"])
    if local_width > 0:
        width = local_width
    local_number_of_apples = int(request.form["apples"])
    if local_number_of_apples > 0:
        number_of_apples = local_number_of_apples
    return "Size updated"


snake_object = Snake()


@app.route("/init")
def init():
    global snake_object
    snake_object = Snake()
    grid_list = (
        snake_object.game_grid.tolist()
    )  # conversion to python list for easier managing of information
    return jsonify(grid_list)  # conversion to json file for the xhr request


@app.route("/direction", methods=["POST"])
def update_direction_object():
    snake_object.update_direction()
    return "", 204


@app.route("/grid", methods=["GET"])
def update_frame_object():
    return snake_object.update_grid()


@app.route("/winning", methods=["GET"])
def send_status_object():
    return snake_object.send_winning_status()

@app.route("/", methods=["GET"])
def index():
    response = make_response(render_template("index.html"))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    app.run("localhost", 7000)


