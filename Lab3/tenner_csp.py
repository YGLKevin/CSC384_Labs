# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete the warehouse domain.

'''
Construct and return Tenner Grid CSP models.
'''

from cspbase import *
import itertools


def adjacent_constraint(var_board, num_of_rows):
    adjacent_direction = [(-1, -1), (-1, 0), (-1, 1)]
    adjacent_constraints = []
    # traverse each cell in the board
    for i in range(num_of_rows):
        for j in range(10):
            for direction in adjacent_direction:
                row_coordinate = i + direction[0]
                col_coordinate = j + direction[1]

                # check if the adjacent cell is out of the boundary
                if num_of_rows > row_coordinate >= 0 and 9 >= col_coordinate >= 0:
                    adjacent_variable = var_board[row_coordinate][col_coordinate]
                    current_variable = var_board[i][j]

                    # get permutation of the domains for these two variables
                    adj_domain = adjacent_variable.domain()
                    cur_domain = current_variable.domain()
                    all_tuples = itertools.product(adj_domain, cur_domain)

                    satisfying_tuples = []
                    # traverse each tuples to check if it satisfies with the constraint
                    for each_tuple in all_tuples:
                        if each_tuple[0] != each_tuple[1]:
                            satisfying_tuples.append(each_tuple)

                    # initialize a constraint
                    adj_constraint = Constraint(
                        "adj_constraint([{}][{}], [{}][{}])".format(row_coordinate, col_coordinate, i, j),
                        [adjacent_variable, current_variable])
                    adj_constraint.add_satisfying_tuples(satisfying_tuples)
                    adjacent_constraints.append(adj_constraint)

    return adjacent_constraints


def row_constraint_m1(var_board, num_of_rows):
    row_constraints = []
    # traverse each cell in the board
    for i in range(num_of_rows):
        for j in range(10):
            row_direction = []

            # only check part of each row for efficiency
            for h in range(j):
                row_direction.append((0, -(h + 1)))
            # print("row_direction:", row_direction)

            for direction in row_direction:
                row_coordinate = i + direction[0]
                col_coordinate = j + direction[1]

                # check if the cell is out of the boundary
                if num_of_rows > row_coordinate >= 0 and 9 >= col_coordinate >= 0:
                    row_variable = var_board[row_coordinate][col_coordinate]
                    current_variable = var_board[i][j]

                    # get permutation of the domains for these two variables
                    row_domain = row_variable.domain()
                    cur_domain = current_variable.domain()
                    all_tuples = itertools.product(row_domain, cur_domain)

                    satisfying_tuples = []
                    # traverse each tuples to check if it satisfies with the constraint
                    for each_tuple in all_tuples:
                        if each_tuple[0] != each_tuple[1]:
                            satisfying_tuples.append(each_tuple)

                    # initialize a constraint
                    row_constraint = Constraint(
                        "row_constraint([{}][{}], [{}][{}])".format(row_coordinate, col_coordinate, i, j),
                        [row_variable, current_variable])
                    row_constraint.add_satisfying_tuples(satisfying_tuples)
                    row_constraints.append(row_constraint)

    return row_constraints


def column_constraint(var_board, num_of_rows, sum_constraint):
    column_constraints = []
    # traverse each column (10 columns for each row) and get all variables for each column
    for a in range(10):
        col_var = []
        for b in range(num_of_rows):
            # get all variables in the current column
            col_var.append(var_board[b][a])

        # get domains of all variables in the column
        col_domain = [var.domain() for var in col_var]
        satisfying_tuples = []
        # get all satisfied tuples for the current column
        for each_tuple in itertools.product(*col_domain):
            if sum(each_tuple) == sum_constraint[a]:
                satisfying_tuples.append(each_tuple)

        # initialize a constraint
        col_constraint = Constraint("col_constraint[{}]".format(a), col_var)
        # add satisfying tuples to the current column constraint
        col_constraint.add_satisfying_tuples(satisfying_tuples)
        # append each column constraint to the total column constraints
        column_constraints.append(col_constraint)

    return column_constraints


def tenner_csp_model_1(initial_tenner_board):
    # ======================== setup ========================
    all_rows = initial_tenner_board[0]
    sum_constraint = initial_tenner_board[1]
    num_of_rows = len(all_rows)
    all_constraints = []
    var_board = [[0 for i in range(10)] for j in range(num_of_rows)]
    all_var = []
    domain = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # ======================== initialize all variables and their domain ========================
    for i in range(num_of_rows):
        for j in range(10):
            each_cell = all_rows[i][j]
            if each_cell == -1:
                var_board[i][j] = Variable("Var[{}][{}]".format(i, j), domain)
            else:
                var_board[i][j] = Variable("Var[{}][{}]".format(i, j), [each_cell])

    # ======================== initialize csp object ========================
    # get all variables
    for each_row in var_board:
        for each_var in each_row:
            all_var.append(each_var)
    # initialize csp object
    csp_object = CSP("model1_csp", all_var)

    # ======================== create row, column and adjacent constraints ========================
    row_c = row_constraint_m1(var_board, num_of_rows)
    column_c = column_constraint(var_board, num_of_rows, sum_constraint)
    adjacent_c = adjacent_constraint(var_board, num_of_rows)
    all_constraints.extend(row_c)
    all_constraints.extend(column_c)
    all_constraints.extend(adjacent_c)

    for c in all_constraints:
        csp_object.add_constraint(c)

    return csp_object, var_board


##############################

def tenner_csp_model_2(initial_tenner_board):
    # ======================== setup ========================
    all_rows = initial_tenner_board[0]
    sum_constraint = initial_tenner_board[1]
    num_of_rows = len(all_rows)
    all_constraints = []
    var_board = [[0 for i in range(10)] for j in range(num_of_rows)]
    all_var = []
    domain = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # ======================== initialize all variables and their domain ========================
    for i in range(num_of_rows):
        for j in range(10):
            each_cell = all_rows[i][j]
            if each_cell == -1:
                var_board[i][j] = Variable("Var[{}][{}]".format(i, j), domain)
            else:
                var_board[i][j] = Variable("Var[{}][{}]".format(i, j), [each_cell])

    # ======================== initialize csp object ========================
    # get all variables
    for each_row in var_board:
        for each_var in each_row:
            all_var.append(each_var)
    # initialize csp object
    csp_object = CSP("model2_csp", all_var)

    # ======================== create row, column and adjacent constraints ========================
    row_c = row_constraint_m2(var_board, num_of_rows)
    column_c = column_constraint(var_board, num_of_rows, sum_constraint)
    adjacent_c = adjacent_constraint(var_board, num_of_rows)
    all_constraints.extend(row_c)
    all_constraints.extend(column_c)
    all_constraints.extend(adjacent_c)

    for c in all_constraints:
        csp_object.add_constraint(c)

    return csp_object, var_board


def row_constraint_m2(var_board, num_of_rows):
    row_constraints = []
    # traverse each row and get all variables for each row
    for a in range(num_of_rows):
        row_var = []
        for b in range(10):
            # get all variables in the current row
            row_var.append(var_board[a][b])

        # get domains of all variables in the row
        row_domain = [var.domain() for var in row_var]
        satisfying_tuples = []
        # get all satisfied tuples for the current row
        for each_tuple in itertools.product(*row_domain):
            count = 0
            for value in each_tuple:
                if each_tuple.count(value) == 1:
                    count += 1
            if count == 10:
                satisfying_tuples.append(each_tuple)

        # initialize a constraint
        row_constraint = Constraint("row_constraint[{}]".format(a), row_var)
        # add satisfying tuples to the current column constraint
        row_constraint.add_satisfying_tuples(satisfying_tuples)
        # append each column constraint to the total column constraints
        row_constraints.append(row_constraint)

    return row_constraints
