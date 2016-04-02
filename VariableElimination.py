from BayesianNetwork import *

##Implement all of the following functions

## Do not modify any of the objects passed in as parameters!
## Create a new Factor object to return when performing factor operations



'''
multiply_factors(factors)

Parameters :
              factors : a list of factors to multiply
Return:
              a new factor that is the product of the factors in "factors"
'''
def multiply_factors(factors):
    new_name = ""
    new_scope = []

    #this list has an entry for each factor.
    var_index_in_mult = [0 for i in range(len(factors))]

    '''
    the entry for factor i will be of len(factors[i].scope).
    if factors = [f, g], f.scope = [x, y], g.scope = [y, z]
    then new_scope will be = [x, y, z]
    var_index_in_mult[0] = [0, 1]

    because the index of x in new_scope is 0, and the index in y of new_scope is 1.

    var_index_in_mult[1] = [1, 2]
    '''

    for fi in range(len(factors)):
        #if factors = [A, B, C] then the name of the new factor will be "A * B * C"
        new_name += factors[fi].name + " * "

        f_scope = factors[fi].get_scope()
        #set the length of the index list for factor f to the right thing.
        var_index_in_mult[fi] = [0 for i in range(len(f_scope))]

        #create the new scope. vi is variable index.
        for vi in range(len(f_scope)):
            if f_scope[vi] not in new_scope:
                new_scope.append(f_scope[vi])
            var_index_in_mult[fi][vi] = new_scope.index(f_scope[vi])

    #now have the name and scope of the new factor, and we know the index of each variable in the new scope.

    mult_fact = Factor(new_name, new_scope)

    '''
    the value of f * g at [X = x, Y = y, Z = z] is f([X=x, Y=y]) * g([Y=y, Z=z])

    for every assignment in the new, multiplied factor ( f*g )
        val = 1
        For factor in [f, g]
            val *= factor(variables from assignment in that factor)

        add the value at that assignment.



    '''

    for assignment in mult_fact.get_assignment_iterator():
        #this will iterate over all possible x,y,z
        #variable values in assignment will be ordered in the same way as variables in new_scope.

        val = 1
        for fi in range(len(factors)):
            #this makes fi_assigns a list with a length equal to the number of variables in
            fi_assigns = [0 for i in range(len(factors[fi].get_scope()))]
            #fi_assings = var_index_in_mult[fi] #this operation might be cheaper, but less clear?

            for vi in range(len(fi_assigns)):
                fi_assigns[vi] = assignment[var_index_in_mult[fi][vi]]

            # populate fi_assigns

            val = val * factors[fi].get_value(fi_assigns)

        mult_fact.add_value_at_assignment(val, assignment)

    return mult_fact

'''
restrict_factor(factor, variable, value):

Parameters :
              factor : the factor to restrict
              variable : the variable to restrict "factor" on
              value : the value to restrict to
Return:
              A new factor that is the restriction of "factor" by
              "variable"="value"
      
              If "factor" has only one variable its restriction yields a 
              constant factor
'''
def restrict_factor(factor, variable, value):

    scope = factor.get_scope()

    if variable not in scope:
        #if the variable to be restricted isn't in the scope of factor,
        #then the restricted factor is the same as the orignal factor.
        #this should probably never happen.
        print("**************YOU HAVE DONE SOMETHING WRONG, THE VARIABLE IS NOT IN THE SCOPE OF THE FACTOR**************")
        return factor

    vi = scope.index(variable)
    new_scope = []
    for v in scope:
        if v != variable:
            new_scope.append(v)

    new_factor = Factor("restricted " + factor.name, new_scope)

    for assignment in factor.get_assignment_iterator():
        if (assignment[vi] == value):
            val = factor.get_value(assignment)

            new_assignment = []
            for index in range(len(assignment)):
                if index != vi:
                    #all elements from old assignment onto the new assignment unless the that element corresponds to the value to be restricted.
                    new_assignment.append(assignment[index])

            new_factor.add_value_at_assignment(val, new_assignment)

    return new_factor

'''
sum_out_variable(factor, variable)

Parameters :
              factor : the factor to sum out "variable" on
              variable : the variable to sum out
Return:
              A new factor that is "factor" summed out over "variable"
'''
def sum_out_variable(factor, variable):
    scope = factor.get_scope()
    vi = scope.index(variable)
    new_scope = []
    for v in scope:
        if v != variable:
            new_scope.append(v)

    new_factor = Factor("var summed out " + factor.name, new_scope)

    #for every assignment in the new factor
    for new_assignment in new_factor.get_assignment_iterator():
        val = 0

        #summing out all the values in the domain of variable.
        for value in variable.domain():
            old_assignment = new_assignment.copy()
            old_assignment.insert(vi, value)
            val += factor.get_value(old_assignment)

        new_factor.add_value_at_assignment(val, new_assignment)

    return new_factor

    
'''
VariableElimination(net, queryVar, evidenceVars)

 Parameters :
              net: a BayesianNetwork object
              queryVar: a Variable object
                        (the variable whose distribution we want to compute)
              evidenceVars: a list of Variable objects.
                            Each of these variables should have evidence set
                            to a particular value from its domain using
                            the set_evidence function. 

 Return:
         A distribution over the values of QueryVar
 Format:  A list of numbers, one for each value in QueryVar's Domain
         -The distribution should be normalized.
         -The i'th number is the probability that QueryVar is equal to its
          i'th value given the setting of the evidence
 Example:

 QueryVar = A with Dom[A] = ['a', 'b', 'c'], EvidenceVars = [B, C]
 prior function calls: B.set_evidence(1) and C.set_evidence('c')

 VE returns:  a list of three numbers. E.g. [0.5, 0.24, 0.26]

 These numbers would mean that Pr(A='a'|B=1, C='c') = 0.5
                               Pr(A='a'|B=1, C='c') = 0.24
                               Pr(A='a'|B=1, C='c') = 0.26
'''       
def VariableElimination(net, queryVar, evidenceVars):

    #1. replace each factor f that mentions variables in evidencVars with its restriction
    factors = net.factors()
    restricted_factors = [0 for i in range(len(factors))]

    for f in factors:
        new_f = f
        for var in evidenceVars:
            if var in f.get_scope():
                new_f = restrict_factor(new_f, var, var.get_evidence())
        restricted_factors[factors.index(f)] = new_f

    #min_fill_ord is a list of variables
    min_fill_ord = min_fill_ordering(restricted_factors, queryVar)

    #for each variable z that is neither evidence nor query
    for z in min_fill_ord:
        #compute the list of factors in restricted_factors that have z in their scope.
        have_z_in_scope = []
        factors_removed = []
        for fi in range(len(restricted_factors)):
            if z in restricted_factors[fi].get_scope():
                have_z_in_scope.append(restricted_factors[fi])
                factors_removed.append(restricted_factors[fi])

        #compute a new factor g that is the product of all factors in F that have z in their scope, summed out over z.
        g = multiply_factors(have_z_in_scope)
        g = sum_out_variable(g, z)
        #remove factors fi from restricted_factors and add factor g.
        for to_remove in factors_removed:
            restricted_factors.remove(to_remove)

        restricted_factors.append(g)

        # we have now removed all factors fi

    #the remaining factors in restricted_factors refer only to the query Q.
    product = multiply_factors(restricted_factors)
    normalization = 0
    values = []

    for assignment in product.get_assignment_iterator():

        values.append(product.get_value(assignment))
        normalization += values[-1]

    for vi in range(len(values)):
        values[vi] = values[vi] / normalization

    return values


