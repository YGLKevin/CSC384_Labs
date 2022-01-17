#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os

from numpy.ma.bench import timer

from search import *  # for search engines
from snowman import SnowmanState, Direction, snowman_goal_state  # for snowball specific classes
from test_problems import PROBLEMS  # 20 test problems


def heur_manhattan_distance(state):
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a snowman state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each snowball that has yet to be stored and the storage point is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.

    manhattan_distance = 0
    dest_position = state.destination
    for snowball in state.snowballs:
        manhattan_distance += abs(snowball[0] - dest_position[0]) + abs(snowball[1] - dest_position[1])

    # print("manhattan_distance=", manhattan_distance)
    # print(state.state_string())
    return manhattan_distance


# HEURISTICS
def trivial_heuristic(state):
    '''trivial admissible snowball heuristic'''
    '''INPUT: a snowball state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''
    return len(state.snowballs)


def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.

    final_heur = 0
    robot_position = state.robot
    dest = state.destination
    new_snowballs_dic = {}
    b_snowball = (0, 0)
    m_snowball = (0, 0)
    s_snowball = (0, 0)

    # find each snowball by its size
    for snowball in state.snowballs:
        if state.snowballs[snowball] == 0:
            b_snowball = snowball
        if state.snowballs[snowball] == 1:
            m_snowball = snowball
        if state.snowballs[snowball] == 2:
            s_snowball = snowball
        if state.snowballs[snowball] == 3 and (snowball[0] != dest[0] or snowball[1] != dest[1]):
            return float("inf")
        if state.snowballs[snowball] == 4 and (snowball[0] != dest[0] or snowball[1] != dest[1]):
            return float("inf")
        if state.snowballs[snowball] == 5:
            return float("inf")

    # find snowballs that are already in destination
    if (b_snowball[0] != dest[0] or b_snowball[1] != dest[1]) and (b_snowball[0] != 0 or b_snowball[1] != 0):
        new_snowballs_dic[0] = b_snowball
    if (m_snowball[0] != dest[0] or m_snowball[1] != dest[1]) and (m_snowball[0] != 0 or m_snowball[1] != 0):
        new_snowballs_dic[1] = m_snowball
    if (s_snowball[0] != dest[0] or s_snowball[1] != dest[1]) and (s_snowball[0] != 0 or s_snowball[1] != 0):
        new_snowballs_dic[2] = s_snowball
    # return 0 when all snowballs are in dest
    if len(new_snowballs_dic) == 0:
        return 0

    # return infinity if either small or medium snowball is in destination and big snowball is not
    if len(new_snowballs_dic) == 2 and new_snowballs_dic.get(0) is not None:
        return float("inf")
    if len(new_snowballs_dic) == 1 and new_snowballs_dic.get(2) is None:
        return float("inf")

    snowballs_keys = sorted(new_snowballs_dic.keys())
    snowball_id = snowballs_keys[0]
    snowball = new_snowballs_dic.get(snowball_id)
    # calculate the manhattan distance between the initial robot position and the snowball position
    final_heur += abs(snowball[0] - robot_position[0]) + abs(snowball[1] - robot_position[1])
    final_heur += heur_manhattan_distance(state)

    return final_heur


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """

    # Many searches will explore nodes (or states) that are ordered by their f-value.
    # For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    # You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    # The function must return a numeric f-value.
    # The value will determine your state's position on the Frontier list during a 'custom' search.
    # You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.

    return sN.gval + weight * sN.hval


def anytime_weighted_astar(initial_state, heur_fn, weight=10., timebound=5):
    # IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of weighted astar algorithm'''

    time_elapsed = 0
    best_fvalue = 0
    previous_weight = weight
    # initialize the search engine with a custom strategy
    se = SearchEngine(strategy='custom', cc_level='full')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initState=initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn,
                   fval_function=wrapped_fval_function)
    # initialize prune and costbound
    costbound = (float("inf"), float("inf"), float("inf"))

    # first time search
    start_time = os.times()[0]
    goal_state = se.search(timebound=timebound, costbound=costbound)
    # check if goal_state would return false for the first time search
    best_state = goal_state
    if goal_state:
        # set up the best f value so far
        best_fvalue = goal_state.gval + heur_fn(goal_state)
    # add search time for the first time search
    end_time = os.times()[0]
    time_elapsed += (end_time - start_time)

    # search till the end
    while time_elapsed < timebound:
        start_time = os.times()[0]
        time_remaining = timebound - time_elapsed

        if goal_state:
            current_fvalue = goal_state.gval + heur_fn(goal_state)
            # prune it when fvalue is greater than and equal to the best fvalue
            if current_fvalue >= best_fvalue:
                costbound = (float("inf"), float("inf"), current_fvalue)
            # update best fvalue and keep searching with the same costbound if a better path found
            elif current_fvalue < best_fvalue:
                best_fvalue = current_fvalue
                best_state = goal_state

            # re-initialize search with updated weight only when weight is changed, no need to re-initialize when weight
            # is not changed
            if weight != previous_weight:
                wrapped_fval_function = (lambda sN: fval_function(sN, weight))
                se.init_search(initState=initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn,
                               fval_function=wrapped_fval_function)

            goal_state = se.search(timebound=time_remaining, costbound=costbound)

        else:
            # return best_state when goal_state is false
            return best_state

        # update the time elapsed
        end_time = os.times()[0]
        search_time = end_time - start_time
        time_elapsed += search_time
        # update weight
        previous_weight = weight
        weight -= 10
        if weight <= 1:
            weight = 1

    return best_state


def anytime_gbfs(initial_state, heur_fn, timebound=5):
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''

    time_elapsed = 0
    best_gvalue = 0
    # initialize the search engine with best-first strategy
    se = SearchEngine(strategy='best_first', cc_level='full')
    se.init_search(initState=initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn)
    # set up costbound and prune
    costbound = (float("inf"), float("inf"), float("inf"))

    # first time search
    start_time = os.times()[0]
    goal_state = se.search(timebound=timebound, costbound=costbound)
    # check if goal_state would return false for the first time search
    best_state = goal_state
    if goal_state:
        # set up the best cost value
        best_gvalue = goal_state.gval
    # add search time for the first time search
    end_time = os.times()[0]
    time_elapsed += (end_time - start_time)

    # search till the end
    while time_elapsed < timebound:
        start_time = os.times()[0]
        time_remaining = timebound - time_elapsed

        if goal_state:
            # prune it when a g(node) is greater than and equal to best gvalue with a new costbound
            if goal_state.gval >= best_gvalue:
                costbound = (goal_state.gval, float("inf"), float("inf"))
            # update best gvalue and keep searching with the same costbound if a better path found
            elif goal_state.gval < best_gvalue:
                best_gvalue = goal_state.gval
                best_state = goal_state
            goal_state = se.search(timebound=time_remaining, costbound=costbound)
        else:
            # return best_state when goal_state is false
            return best_state

        # update the time elapsed
        end_time = os.times()[0]
        search_time = end_time - start_time
        time_elapsed += search_time

    return best_state
