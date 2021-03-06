"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    return custome_heristic_score_two(game, player)

#compare the differential of legal_moves with total blank spaces, game with high ratio leads better outcomes
# ID_Improved         62.86%
# Student            67.14%
def custom_heuristic_score_one(game, player):
    blank_spaces = len(game.get_blank_spaces())
    score = float(len(game.get_legal_moves(player)) * 3 - len(game.get_legal_moves(game.get_opponent(player))) * 2)
    return score / blank_spaces

# Based on the differential of player's legal moves and opponent's legal moves, add the check of
# how many new legal moves it leads to with forecast every legal moves,
# compare the sum of new legal moves between the player and it's opponent
# ID_Improved         65.71%
# Student             76.43%
def custome_heristic_score_two(game, player):
    player_newgame = [(game.forecast_move(move)) for move in game.get_legal_moves(player)]
    opponent_player_newgame = [(game.forecast_move(move)) for move in game.get_legal_moves(game.get_opponent(player))]
    game_diff = float(len(game.get_legal_moves(player)) - len(game.get_legal_moves(game.get_opponent(player))))
    forecast_move_game_diff = sum([len(game.get_legal_moves(game.inactive_player)) for game in player_newgame]) - \
                              sum([len(game.get_legal_moves(game.active_player)) for game in opponent_player_newgame])
    return game_diff + forecast_move_game_diff

#Based on the differential of player's legal moves and opponent's legal moves, give addional score if moves results in center
# ID_Improved         60.00%
# Student             66.43%

def custome_heristic_score_three(game, player):
    center = [(x, y) for x in [2, 3, 4] for y in [2, 3, 4]]
    blank_spaces = len(game.get_blank_spaces())
    player_moves = game.get_legal_moves(player)
    opponent_player_moves = game.get_legal_moves(game.get_opponent(player))
    player_center_moves = len([move for move in player_moves if move in center])
    opponent_player_center_moves = len([move for move in opponent_player_moves if move in center])
    return len(player_moves) + player_center_moves - len(opponent_player_moves) - opponent_player_center_moves



class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=1, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        if len(legal_moves) == 0:
            return (-1, -1)

        #give best move a random legal move in case iterative true but time is limit
        best_move = random.choice(legal_moves)
        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.iterative:
                depth = 1
                while True:
                    _, best_move = getattr(self, self.method)(game, depth)
                    depth += 1
            else:
                _, best_move = getattr(self, self.method)(game, self.search_depth)

        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        moves = game.get_legal_moves()
        #terminal test
        if depth == 0:
            return self.score(game, self), game.get_player_location(game.inactive_player)

        #get utility when reach the terminal
        if len(moves) == 0:
            return self.score(game, self), (-1, -1)

        best_move = ()
        if maximizing_player:
            best_score = float('-inf')
            for move in moves:
                (_score, _) = self.minimax(game.forecast_move(move), depth - 1, False)
                best_score = max(best_score, _score)
                if best_score == _score:
                    best_move = move
            return best_score, best_move
        else:
            best_score = float('inf')
            for move in moves:
                (_score, _) = self.minimax(game.forecast_move(move), depth - 1, True)
                best_score = min(best_score, _score)
                if best_score == _score:
                    best_move = move
            return best_score, best_move


    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.

        self_notes: from AI book
        α = the value of the best (i.e., highest-value) choice we have found so far at any choice point along the path for MAX.

        β = the value of the best (i.e., lowest-value) choice we have found so far at any choice point along the path for MIN.

        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        moves = game.get_legal_moves()

        #terminal test
        if depth == 0:
            return self.score(game, self), game.get_player_location(game.inactive_player)

        #get utility when reach the terminal
        if len(moves) == 0:
            return self.score(game, self), (-1, -1)

        best_move = ()
        if maximizing_player:
            best_score = float('-inf')
            for move in moves:
                (_score, _) = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, False)
                best_score = max(_score, best_score)
                if best_score == _score:
                    best_move = move
                if best_score >= beta:
                    return best_score, best_move
                alpha = max(alpha, best_score)
            return best_score, best_move
        else:
            best_score = float('inf')
            for move in moves:
                (_score, _) = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, True)
                best_score = min(_score, best_score)
                if best_score == _score:
                    best_move = move
                if best_score <= alpha:
                    return best_score, best_move
                beta = min(beta, best_score)
            return best_score, best_move
