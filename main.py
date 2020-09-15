# write your code here
from itertools import chain
from random import choice


class Field:
    game_states = ["Game not finished", "Draw", "wins"]
    winning_patterns = {"X": ["X", "X", "X"], "O": ["O", "O", "O"]}

    def __init__(self, dimension):
        self.dimension = dimension
        self.field = [["_", "_", "_"], ["_", "_", "_"], ["_", "_", "_"]]
        self.winner = ""
        self.game_state = self.game_states[0]

    def __str__(self):
        str_ = "---------"
        for line in self.field:
            str_ += "\n| "
            str_ += " ".join([c for c in line])
            str_ += " |"
        str_ += "\n---------"
        return str_

    def input_in_range(self, *args):
        """
        The function checks the correctness of entered coordinates to be them in the range
        :param args: (str) coordinates
        :return: (bool) True if correct
        """
        if not all([0 < int(i) <= self.dimension for i in args]):
            print(f"Coordinates should be from 1 to {self.dimension}!")
            return False
        return True

    def check_cell_occupied(self, *args):
        """
        The function checks if the cell under the given coordinates is already occupied
        :param args: (int) coordinates
        :return: (bool) True if occupied
        """
        if self.field[args[0]][args[1]] != "_":
            print("This cell is occupied! Choose another one!")
            return True

    def free_cells(self):
        """
        The function prepares a list of all available cells
        :return: list of lists with coordinates of free cells
        """
        return [[i, k] for i in range(3) for k in range(3) if self.field[i][k] == "_"]

    def check_game_state(self):
        """
        The function checks if there draw or win on the given field
        :return:
        """
        vertical = self.vertical_field()
        diagonals = self.diagonals()
        for player, condition in Field.winning_patterns.items():
            if condition in chain(self.field, vertical, diagonals):
                self.winner = player
                self.game_state = Field.game_states[2]  # win
                return

        if not self.has_empty_cells():
            self.game_state = Field.game_states[1]  # draw
        else:
            self.game_state = Field.game_states[0]  # game not finished
        self.winner = ""

    def vertical_field(self):
        """
        The functions converts rows of the field into columns
        :return: list of lists
        """
        ver_field = [["_", "_", "_"], ["_", "_", "_"], ["_", "_", "_"]]
        k = 0
        for line in self.field:
            for i in range(3):
                ver_field[i][k] = line[i]
            k += 1
        return ver_field

    def diagonals(self):
        """
        The function takes and returns two diagonals of the field
        :return: list of lists
        """
        first_diagonal = [self.field[i][i] for i in range(3)]
        second_diagonal = [self.field[2][0], self.field[1][1], self.field[0][2]]
        return [first_diagonal, second_diagonal]

    def has_empty_cells(self):
        for line in self.field:
            if "_" in line:
                return True

    def mark_cell(self, player, *args):
        self.field[args[0]][args[1]] = player


class Player:

    def __init__(self, move_symbol):
        self.move_symbol = move_symbol


class Human(Player):

    def make_move(self, field):
        while True:
            coord = input("Enter the coordinates: ").split()
            if input_isdigit(*coord) and field.input_in_range(*coord):
                adopted_coord = [-int(coord[1]), int(coord[0]) - 1]
                if not field.check_cell_occupied(*adopted_coord):
                    break
        field.mark_cell(self.move_symbol, *adopted_coord)


class AI(Player):

    def make_move(self, field):
        ai_coord = choice(field.free_cells())
        field.mark_cell(self.move_symbol, *ai_coord)


class EasyAI(AI):

    def make_move(self, field):
        print('Making move level "easy"')
        super().make_move(field)


class MediumAI(AI):
    patterns = [["X", "X", "_"], ["X", "_", "X"], ["_", "X", "X"], ["O", "O", "_"], ["O", "_", "O"], ["_", "O", "O"]]

    def make_move(self, field):
        print('Making move level "medium"')
        if self.check_possibilities(field):
            pass
        else:
            super().make_move(field)

    def check_possibilities(self, field):
        vertical = field.vertical_field()
        diagonals = field.diagonals()
        for cell in field.free_cells():
            if any([self.check_horizontal(field.field, cell),
                    self.check_vertical(vertical, cell),
                    self.check_diagonal(diagonals, cell)]):
                field.mark_cell(self.move_symbol, *cell)
                return True

    def check_horizontal(self, field, cell):
        line = field[cell[0]]
        if line in self.patterns:
            return True

    def check_vertical(self, field, cell):
        line = field[cell[1]]
        if line in self.patterns:
            return True

    def check_diagonal(self, diagonals, cell):
        if cell == [1, 1]:
            for diagonal in diagonals:
                if diagonal in self.patterns:
                    return True
        if cell in [[0, 0], [2, 2]]:
            if diagonals[0] in self.patterns:
                return True
        if cell in [[2, 0], [0, 2]]:
            if diagonals[1] in self.patterns:
                return True


class HardAI(AI):

    def make_move(self, field):
        new_field = Field(3)
        scores_of_moves = []
        new_field.field = field.field.copy()
        available_spots = field.free_cells()

        for cell in available_spots:
            scores_of_moves.append(self.get_score(new_field, True, *cell))

        best_move_index = scores_of_moves.index(max(scores_of_moves))
        cell = available_spots[best_move_index]
        print('Making move level "hard"')
        field.mark_cell(self.move_symbol, *cell)

    def minimax(self, board, player):
        """
        The function recursively tries out every possible move and its outcomes
        :param board: (list of lists) it's the copy of the original board, used to try out moves on it
        :param player: (bool) where True is maximizer and False is minimizer
        :return: (int) score
        """
        board.check_game_state()
        if board.game_state == Field.game_states[1]:  # draw
            return 0
        if board.winner and board.winner != self.move_symbol:  # lose
            return -10
        if board.winner == self.move_symbol:  # win
            return 10

        available_spots = board.free_cells()
        scores_of_moves = []

        for cell in available_spots:
            if player:
                score = self.get_score(board, False, *cell)
                if score == -10:  # alpha-beta pruning
                    return score
            else:
                score = self.get_score(board, True, *cell)
                if score == 10:  # # alpha-beta pruning
                    return score
            scores_of_moves.append(score)

        if player:
            return min(scores_of_moves)
        return max(scores_of_moves)

    def get_score(self, field, player, *cell):
        if player:
            symbol = "X" if self.move_symbol == "X" else "O"
        else:
            symbol = "O" if self.move_symbol == "X" else "X"
        field.mark_cell(symbol, *cell)
        score = self.minimax(field, player)
        field.mark_cell("_", *cell)
        return score


def input_isdigit(*args):
    if not all([i.isdigit() for i in args]):
        print("You should enter numbers!")
        return False
    return True


def open_menu():
    while True:
        exit_game = menu()
        if exit_game:
            break


def menu():
    """
    menu prompts user to enter the command.
    Two possible commands:
        'exit' to exit the game
        'start player1 player2' to start the game with defined players, where 'user' is a human player and
        'easy', 'medium' and 'hard' is a difficulty level of AI. Player1 makes first move with 'X'
    :return: (bool) True if exit game
    """
    command = input("Input command: ").split()
    if command[0] == "start":
        if len(command) == 3 and all([(command[i] in ["user", "easy", "medium", "hard"]) for i in range(1, 3)]):
            start_game(*command[1:])  # start game with defined players
        else:
            print("Bad parameters!")
    elif command[0] == "exit":
        return True
    else:
        print("Bad parameters!")


def start_game(*args):
    """
    The function initiate an object for each player
    :param args: (list of str) players to create
    :return: None
    """
    players = list()
    symbol = "X"  # for the first player

    for player in args:
        if player == "user":
            players.append(Human(symbol))
        elif player == "easy":
            players.append(EasyAI(symbol))
        elif player == "medium":
            players.append(MediumAI(symbol))
        elif player == "hard":
            players.append(HardAI(symbol))
        symbol = "O"  # for the second player
    make_moves(*players)


def make_moves(*players):
    """
    Players make moves until the game is finished
    :param players: (list of Player)
    :return: None
    """
    field = Field(3)
    print(field)  # print the empty field
    number = 0
    while True:
        players[number].make_move(field)
        print(field)
        field.check_game_state()
        if field.game_state != Field.game_states[0]:
            break
        number = 1 if number == 0 else 0  # switch the player

    if field.game_state == Field.game_states[2]:  # if one player wins
        print(field.winner, field.game_state)
    else:  # if draw
        print(field.game_state)


open_menu()
