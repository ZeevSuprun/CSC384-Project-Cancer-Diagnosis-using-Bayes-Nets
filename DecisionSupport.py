#Implement the function DecisionSupport

'''
For this question you may use the code from part 1

Note however that part 2 will be marked independent of part 1

The solution for VariableElimination.py will be used for testing part2 instead
of the copy you submit. 
'''

from MedicalBayesianNetwork import *
from VariableElimination import *

'''
Parameters:
             medicalNet - A MedicalBayesianNetwork object                        

             patient    - A Patient object
                          The patient to calculate treatment-outcome
                          probabilites for
Return:
         -A factor object

         This factor should be a probability table relating all possible
         Treatments to all possible outcomes
'''
def DecisionSupport(medicalNet, patient):
    # output a conditional probability table relating the treatment variables to the outcome variables.

    # patient has evidence values and variables.
    # assuming all the patient variables are Treatment variables.

    full_factor_table = multiply_factors(medicalNet.net.factors())
    full_scope = full_factor_table.get_scope()
    #full_factor table is now a factor table containing all variables in the medical net.

    #Now to restrict factor table based on evidence.
    restricted_table = full_factor_table

    evidenceVars = patient.evidenceVariables()
    evidenceVals = patient.evidenceValues()
    for var in evidenceVars:
            if var in full_scope:
                restricted_table = restrict_factor(restricted_table, var, evidenceVals[evidenceVars.index(var)])

    #declaring these as variables outside the for loop makes things a bit faster.
    treatment_vars = medicalNet.getTreatmentVars()
    outcome_vars = medicalNet.getOutcomeVars()
    for v in restricted_table.get_scope():
        if (v not in treatment_vars and v not in outcome_vars):
            restricted_table = sum_out_variable(restricted_table, v)

    #restricted table now has all of the correct variables in it.
    restricted_scope = restricted_table.get_scope()

    given = Factor("given", treatment_vars)
    outcome = Factor("outcome", outcome_vars)

    #we're representing a conditional distribution, so now we need to normalize.
    #we need to make it so all P(A | B = b) sums to 1

    #the normalized version of restricted table, since you can't change values in-place. (I think.)
    normalizedFactor = Factor("Normalized Factor", restricted_table.get_scope())

    #Since we aren't iterating through all of the assignments in
    var_list = outcome_vars + treatment_vars
    index_list = [0 for i in range(len (var_list))]

    for i in range(len(var_list)):
        index_list[i] = restricted_scope.index(var_list[i])
    #index_list[i] = the index in assignment of var_list[i]

    #in the following nested for loops we will need to rearrange input + output variable ordering
    #into an assignment ordering. index_list will help with that.

    for treatment_assignment in given.get_assignment_iterator():
        #Each iteration of this loop is a set of the given values.
        #so if restricted_factors is supposed to represent P(A, B | C, D),
        #this will iterate through all combinations of C and D.
        #Sum P(A, B | C = c, D = d) over all A, B must equal to 1.

        sum = 0
        for outcome_assignment in outcome.get_assignment_iterator():

            #step 1: get the assignment from outcome_assignment and treatment_assignment
            assignment = [0 for i in range(len(var_list))]
            var_list = outcome_assignment + treatment_assignment

            for i in range(len(var_list)):
                #index_list[i] = the index in assignment of var_list[i]
                assignment[index_list[i]] = var_list[i]

            sum += restricted_table.get_value(assignment)

        #now that the sum is known, we populate the normalized assignments by dividing everything by the sum.
        for outcome_assignment in outcome.get_assignment_iterator():
            #figure out how to get assignment again.
            #step 1: get the assignment from outcome_assignment and treatment_assignment
            assignment = [0 for i in range(len(var_list))]
            var_list = outcome_assignment + treatment_assignment

            for i in range(len(var_list)):
                #index_list[i] = the index in assignment of var_list[i]
                assignment[index_list[i]] = var_list[i]

            val = restricted_table.get_value(assignment) / sum
            normalizedFactor.add_value_at_assignment(val, assignment)

    return normalizedFactor
