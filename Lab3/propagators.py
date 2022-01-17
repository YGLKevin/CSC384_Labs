#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method).
      bt_search NEEDS to know this in order to correctly restore these
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated
        constraints)
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.


var_ordering == a function with the following template
    var_ordering(csp)
        ==> returns Variable

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.
   '''

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable, value pairs and return '''

    if newVar is None:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)

    #remove all constraints that have more than 1 uninstantiated variable remaining
    filtered_constraints = []
    for c in constraints:
        if c.get_n_unasgn() == 1:
            filtered_constraints.append(c)

    pruned_values = []
    #traverse filtered all constraints
    for c in filtered_constraints:
        unassigned_var = c.get_unasgn_vars()[0]
        values = unassigned_var.cur_domain()
        #traverse all values in the given unassigned variable
        for d in values:
            #check if assignment unassigned_var=d satisfies the constraint
            if not c.has_support(unassigned_var, d):
                #prune the value if not
                unassigned_var.prune_value(d)
                #store it
                pruned_values.append((unassigned_var, d))
        #return if the current variable is DWO
        if unassigned_var.cur_domain_size() == 0:
            return False, pruned_values  # Domain Wipe Out
    return True, pruned_values


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''

    if newVar is None:
        GAC_Queue = csp.get_all_cons()
    else:
        GAC_Queue = csp.get_cons_with_var(newVar)

    pruned_values = []
    #traverse the GAC_Queue until it's empty
    while len(GAC_Queue) != 0:
        #get first constraint in the queue
        c = GAC_Queue.pop(0)
        unassigned_variables = c.get_unasgn_vars()
        #traverse each member of scope(c)
        for variable in unassigned_variables:
            values = variable.cur_domain()
            #traverse each value of the variable
            for d in values:
                if not c.has_support(variable, d):
                    # prune the value if not
                    variable.prune_value(d)
                    # store it
                    pruned_values.append((variable, d))
                    #check if current domain is empty
                    if variable.cur_domain_size() == 0:
                        GAC_Queue = []
                        return False, pruned_values
                    else:
                        #get all impacted constraints that include the given variable
                        impacted_constraints = csp.get_cons_with_var(variable)
                        #traverse all constraint in impacted_constraints and only append non-duplicates to GAC_Queue
                        for constraint in impacted_constraints:
                            if constraint not in GAC_Queue:
                                GAC_Queue.append(constraint)

    return True, pruned_values


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    unassigned_variables = csp.get_all_unasgn_vars()
    sorted_list = []
    for var in unassigned_variables:
        num_of_remaining_values = var.cur_domain_size()
        sorted_list.append((var, num_of_remaining_values))

    #sort the list based on the num_of_remaining_values of each variable in an Ascending order
    sorted_list = sorted(sorted_list, key=lambda sorted_list: sorted_list[1], reverse=False)
    #get the first one
    optimal_var = sorted_list.pop(0)[0]

    return optimal_var

