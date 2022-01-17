# The tagger.py starter code for CSC384 A4.
# Currently reads in the names of the training files, test file and output file,
# and calls the tagger (which you need to implement)
import os
import sys
import time

def tag(training_list, test_file, output_file):
    # Tag the words from the untagged input file and write them into the output file.
    # Doesn't do much else beyond that yet.
    print("Tagging the file.")

    # get the start time
    start_time = time.time()

    # get the test file
    t_file = open(test_file, 'r')
    test_data = t_file.readlines()
    # create a output file
    out_file = open(output_file, 'w')

    # get all training files and combine them into one list
    total_training_data = []
    for file in training_list:
        training_file = open(file, 'r')
        training_file = training_file.readlines()
        total_training_data += training_file

    # get all tags, all pos
    all_tags = set()
    all_pos = set()
    initial_prob = dict()
    for entry in total_training_data:
        pos = entry.split()[0]
        all_pos.add(pos)
        pos_tag = entry.split()[2]
        all_tags.add(pos_tag)
        # set up a dict for count the occurrences of each tag
        initial_prob[pos_tag] = float(0)

    # create a 2D matrix to store the emission probability
    # initialize all occurrences to 0
    emission_matrix = dict()
    for pos in all_pos:
        temp = dict()
        for pos_tag in all_tags:
            temp[pos_tag] = float(0)
        emission_matrix[pos] = temp

    # create a 2D matrix for the transition probability
    transition_matrix = dict()
    # assume the inner dict is the current state, and the outer dict is the previous dict
    for pos_tag1 in all_tags:
        temp = dict()
        for pos_tag2 in all_tags:
            temp[pos_tag2] = float(0)
        transition_matrix[pos_tag1] = temp

    # count the occurrence of each entry, and get the occurrences of each tag
    count = 0
    for i in range(len(total_training_data)):
        pos = total_training_data[i].split()[0]
        pos_tag = total_training_data[i].split()[2]
        # count occurrence of each line
        emission_matrix[pos][pos_tag] += 1
        # count the occurrences of each tag
        initial_prob[pos_tag] += 1
        # count the occurrences of the tuple [x(t), x(t-1)]
        # skip for the first iteration
        if i != 0:
            count += 1
            transition_matrix[previous_tag][pos_tag] += 1
        previous_tag = pos_tag

    # get the initial probability of each tag
    total_occurrence = sum(initial_prob.values())
    for each_tag in initial_prob:
        initial_prob[each_tag] = initial_prob[each_tag] / total_occurrence

    # ---------emission matrix---------
    for each_pos in emission_matrix:
        # get the sum of each pos's occurrence
        sum_of_pos_occurrence = sum(emission_matrix[each_pos].values())
        # calculate the emission probability of each tag for a pos and store it back to the matrix
        for each_tag in emission_matrix[each_pos]:
            emission_prob = emission_matrix[each_pos][each_tag] / sum_of_pos_occurrence
            # for unseen examples, their emission probability should be a very small number
            if emission_prob == 0:
                emission_prob = float(0.001)
            emission_matrix[each_pos][each_tag] = emission_prob

    # ---------transition matrix---------
    for each_prev_tag in transition_matrix:
        # get the sum of each pos tag's occurrence
        sum_of_tag_occurrence = sum(transition_matrix[each_prev_tag].values())
        # calculate the transition probability
        for each_current_tag in transition_matrix[each_prev_tag]:
            transition_matrix[each_prev_tag][each_current_tag] = transition_matrix[each_prev_tag][each_current_tag] / sum_of_tag_occurrence

    # ------------------Running Viterbi algorithm to find the most likely sequence of tags based on the given test data----------------
    path_trellis = viterbi(test_data, all_tags, all_pos, initial_prob, transition_matrix, emission_matrix)

    # for each pos from the test file, get its corresponding tag from the emission matrix
    tagged_output = []
    line_format = "{} : {}\n"
    for i in range(len(test_data)):
        each_line = test_data[i].rstrip()
        tagged_output.append(line_format.format(each_line, path_trellis[i]))

    # write the solution to the output file
    out_file.writelines(tagged_output)
    out_file.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Total Time Elapsed: {:.2f} min".format(round(elapsed_time / 60, 2)))


# observation_space: a list that has all pos from the test file
# state_space: all tags that appeared in the training files
# training_observation_space: all pos that appeared in the training files
# initial_prob: initial_prob
# transition_matrix: transition_matrix
# emission_matrix: emission_matrix
def viterbi(observation_space, state_space, training_observation_space, initial_prob, transition_matrix, emission_matrix):
    print("Running Viterbi.....")
    start_time = time.time()

    # create a 2D matrix for storing maximum probabilities
    prob_trellis = [[float(0) for i in range(len(observation_space))] for j in range(len(state_space))]
    # a list for storing the most likely tag sequence based on the given observations
    path_trellis = []

    # determine trellis values for the first state
    s = 0
    sum_prob = 0
    max_prob = 0
    max_prob_state = ''
    for state in state_space:
        # for unseen pos, calculate the prob only with the initial prob
        if observation_space[0].rstrip() not in training_observation_space:
            emission_prob = 1
        else:
            emission_prob = emission_matrix[observation_space[0].rstrip()][state]
        # calculate the probabilities for the first column (X1)
        prob_trellis[s][0] = initial_prob[state] * emission_prob
        sum_prob += prob_trellis[s][0]
        if prob_trellis[s][0] > max_prob:
            max_prob = prob_trellis[s][0]
            max_prob_state = state
        s += 1
    path_trellis.append(max_prob_state)

    # normalization for the first column
    for i in range(len(state_space)):
        prob_trellis[i][0] = prob_trellis[i][0] / sum_prob

    # traverse each given pos and calculate the most likely tag for that pos and store the tag sequence into path_trellis
    for o in range(1, len(observation_space)):
        s1 = 0
        sum_column_prob = 0
        max_state = ''
        max_curr_column_prob = 0
        # for each current state, calculate the max probability for each previous states
        for current_state in state_space:
            s2 = 0
            # given a current state, calculate the probabilities based on each previous state, and find the max prob
            max_prob = 0
            for previous_state in state_space:
                # for unseen pos, calculate the prob with the initial prob and the transition prob
                if observation_space[o].rstrip() not in training_observation_space:
                    prob = prob_trellis[s2][o-1] * transition_matrix[previous_state][current_state]
                else:
                    prob = prob_trellis[s2][o-1] * transition_matrix[previous_state][current_state] * emission_matrix[observation_space[o].rstrip()][current_state]
                # update the max prob
                if prob > max_prob:
                    max_prob = prob
                s2 += 1
            prob_trellis[s1][o] = max_prob
            sum_column_prob += max_prob
            # update the max_curr_column_prob
            if prob_trellis[s1][o] > max_curr_column_prob:
                max_curr_column_prob = prob_trellis[s1][o]
                max_state = current_state
            s1 += 1

        # update the path with the max prob in the current column
        path_trellis.append(max_state)

        # for each column in the prob_trellis, we need to normalize them (all probabilities in the same column should add to 1)
        for i in range(len(state_space)):
            prob_trellis[i][o] = prob_trellis[i][o] / sum_column_prob

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Viterbi Time Elapsed: {:.2f} min".format(round(elapsed_time / 60, 2)))

    return path_trellis


if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training files> -t <test file> -o <output file>"
    parameters = sys.argv
    training_list = parameters[parameters.index("-d")+1:parameters.index("-t")]
    test_file = parameters[parameters.index("-t")+1]
    output_file = parameters[parameters.index("-o")+1]
    # print("Training files: " + str(training_list))
    # print("Test file: " + test_file)
    # print("Ouptut file: " + output_file)

    # Start the training and tagging operation.
    tag(training_list, test_file, output_file)