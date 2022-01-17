"""
An AI player for Othello.
"""

"""
Description of my own heuristic:

I implemented 3 customized heuristics:
1. Coin Parity: Heuristic value is the difference between the number of White pieces and the number of Black pieces.
2. Mobility: number of moves  each player have available to them
3. Corners: Assign value to edge positions, especially corners 

The final heuristic is the sum of these three heuristic values.

"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

# global dictionary to cache states
minimax_min_dict = {}
minimax_max_dict = {}
alphabeta_min_dict = {}
alphabeta_max_dict = {}

def take_third(elem):
    return elem[2]

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)
    num_of_black = score[0]
    num_of_white = score[1]

    if color == 1:
        utility_value = num_of_black - num_of_white
    else:
        utility_value = num_of_white - num_of_black

    return utility_value


# Better heuristic value of board
def compute_heuristic(board, color):

    # ===============1. Coin Parity===============:
    score = get_score(board)
    num_of_black = score[0]
    num_of_white = score[1]
    if color == 1:
        heuristic_1 = num_of_black - num_of_white
    else:
        heuristic_1 = num_of_white - num_of_black

    # ===============2. Mobility===============:
    heuristic_2 = len(get_possible_moves(board, color))

    # ===============3. Corners===============:
    count = 0
    board_dimension = len(board) - 1
    corners = [(0, 0), (0, board_dimension), (board_dimension, 0), (board_dimension, board_dimension)]
    for corner in corners:
        if board[corner[0]][corner[1]] == color:
            count += 1
    heuristic_3 = count * 10

    # ===============4. Final heuristic===============:
    final_heuristic = heuristic_1 + heuristic_2 + heuristic_3

    return final_heuristic

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):

    # check if the given state has already existed in the cache
    if caching == 1 and (board, color) in minimax_min_dict:
        best_move, utility = minimax_min_dict[(board, color)]
        return best_move, utility

    # find opponent's color
    if color == 1:
        opponent_color = 2
    else:
        opponent_color = 1

    # initialization
    possible_moves = get_possible_moves(board, opponent_color)
    min_utility = float("inf")

    # terminate when there is no possible moves or reaches the depth limit
    if possible_moves == [] or limit == 0:
        best_move, utility = None, compute_utility(board, color)
        if caching == 1:
            minimax_min_dict[(board, color)] = best_move, utility
        return best_move, utility

    best_move = possible_moves[0]

    for move in possible_moves:
        next_board = play_move(board, opponent_color, move[0], move[1])
        next_move, next_utility = minimax_max_node(next_board, color, limit-1, caching)

        # compare the new utility with the current beta: update when we found a smaller one
        if min_utility > next_utility:
            best_move, min_utility = move, next_utility

    # cache the state with best move and its utility value
    if caching == 1:
        minimax_min_dict[(board, color)] = best_move, min_utility

    return best_move, min_utility

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility

    # check if the given state has already existed in the cache
    if caching == 1 and (board, color) in minimax_max_dict:
        best_move, utility = minimax_max_dict[(board, color)]
        return best_move, utility

    # initialization
    possible_moves = get_possible_moves(board, color)
    max_utility = float("-inf")

    # terminate when there is no possible moves or reaches the depth limit
    if possible_moves == [] or limit == 0:
        best_move, utility = None, compute_utility(board, color)
        if caching == 1:
            minimax_max_dict[(board, color)] = best_move, utility
        return best_move, utility

    best_move = possible_moves[0]

    # traverse each possible move that Max player can choose
    for move in possible_moves:
        # get new board based on the given move
        next_board = play_move(board, color, move[0], move[1])
        # current level is max, so the next level should be min
        next_move, next_utility = minimax_min_node(next_board, color, limit-1, caching)

        # compare the new utility with the current beta: update when we found a bigger one
        if max_utility < next_utility:
            best_move, max_utility = move, next_utility

    # cache the state with best move and its utility value
    if caching == 1:
        minimax_max_dict[(board, color)] = best_move, max_utility

    return best_move, max_utility

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """

    # always return the move with the maximum utility
    best_move, _ = minimax_max_node(board, color, limit, caching)

    return best_move

################################################# ALPHA-BETA PRUNING ###############################################################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    # check if the given state has already existed in the cache
    if caching == 1 and (board, color) in alphabeta_min_dict:
        best_move, utility = alphabeta_min_dict[(board, color)]
        return best_move, utility

    # find opponent's color
    if color == 1:
        opponent_color = 2
    else:
        opponent_color = 1

    # initialization
    possible_moves = get_possible_moves(board, opponent_color)
    board_cache = []
    min_utility = float("inf")

    # terminate when there is no possible moves or reaches the depth limit
    if possible_moves == [] or limit == 0:
        best_move, utility = None, compute_utility(board, color)
        if caching == 1:
            alphabeta_min_dict[(board, color)] = best_move, utility
        return best_move, utility

    best_move = possible_moves[0]

    # sort the board cache based on its utility (ascending order) when ordering is true
    for move in possible_moves:
        new_board = play_move(board, opponent_color, move[0], move[1])
        board_utility = compute_utility(new_board, opponent_color)
        board_cache.append((new_board, move, board_utility))

    if ordering == 1:
        board_cache = sorted(board_cache, key=take_third, reverse=False)
        # print("sorted:", board_cache)

    # traverse each board in the sorted board cache
    for each_tuple in board_cache:
        next_board = each_tuple[0]
        move = each_tuple[1]
        next_move, next_utility = alphabeta_max_node(next_board, color, alpha, beta, limit-1, caching, ordering)

        # compare the new utility with the current beta: update when we found a smaller one
        if min_utility > next_utility:
            best_move, min_utility = move, next_utility
        # stop expanding the rest of the children of the current node when minimum utility found so far(min_utility) is
        # bigger than or equal to the utility of a children node
        if min_utility <= alpha:
            return best_move, min_utility
        beta = min(beta, min_utility)

    # cache the state with best move and its utility value
    if caching == 1:
        alphabeta_min_dict[(board, color)] = best_move, min_utility

    return best_move, min_utility

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    # check if the given state has already existed in the cache
    if caching == 1 and (board, color) in alphabeta_max_dict:
        best_move, utility = alphabeta_max_dict[(board, color)]
        return best_move, utility

    # initialization
    possible_moves = get_possible_moves(board, color)
    board_cache = []
    max_utility = float("-inf")

    # terminate when there is no possible moves or reaches the depth limit
    if possible_moves == [] or limit == 0:
        best_move, utility = None, compute_utility(board, color)
        if caching == 1:
            alphabeta_max_dict[(board, color)] = best_move, utility
        return best_move, utility

    best_move = possible_moves[0]

    # sort the board cache based on its utility (ascending order) when ordering is true
    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        board_utility = compute_utility(new_board, color)
        board_cache.append((new_board, move, board_utility))
        # print("sorted:", board_cache)

    if ordering == 1:
        board_cache = sorted(board_cache, key=take_third, reverse=True)

    # traverse each board in the sorted board cache
    for each_tuple in board_cache:
        next_board = each_tuple[0]
        move = each_tuple[1]
        next_move, next_utility = alphabeta_min_node(next_board, color, alpha, beta, limit - 1, caching, ordering)

        # compare the new utility with the current beta: update when we found a smaller one
        if max_utility < next_utility:
            best_move, max_utility = move, next_utility
        # stop expanding the rest of the children of the current node when maximum utility found so far(max_utility) is
        # smaller than or equal to the utility of a children node
        if max_utility >= beta:
            return best_move, max_utility
        alpha = max(alpha, max_utility)

    # cache the state with best move and its utility value
    if caching == 1:
        alphabeta_max_dict[(board, color)] = best_move, max_utility

    return best_move, max_utility

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """

    best_move, _ = alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)

    return best_move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
