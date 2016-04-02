from BayesianNetwork import *
from VariableElimination import *


def create_conditional_factor (required_var, given_var_list, dataset):
    '''
    Given a required variable, a list of given variables, and a dataset.
    Each element in dataset is a line from data.txt.

    this function will create a conditional probability factor that is a table of values for
    P(required_var | given_var_list)
    using the dataset to compute this probability.

    '''

    new_factor = Factor("new_factor", [required_var] + given_var_list)
    given = Factor("given", given_var_list)


    assignments = list(given.get_assignment_iterator())
    examples_with_assignment = [ [] for i in range(len(assignments))]
    for example in dataset:

        #Determine which assignment of the given vars this example corresponds to.
        this_assignment = []
        for var in given_var_list:
            this_assignment.append( example[int(var.name[0])] )

        #the index of this assignment in the list of assignments.
        index = assignments.index(this_assignment)
        examples_with_assignment[index].append(example)

    for index in range(len(assignments)):

        num_examples = len(examples_with_assignment[index])
        #print(num_examples)
        num_each_value = [0 for i in range(11)]
        #find the number of times each value in the domain of required_variable appears for this assignment of the given variables.
        for ex in examples_with_assignment[index]:
            #find the value of required_var in ex

            val = ex[ int(required_var.name[0]) ]
            num_each_value[val] += 1

        #for every element in dataset that gives the given variables the assigned values
        #print(num_each_value)
        #print("\n")
        for val in required_var.domain():

            # P(required_var = val | this assignment of the given vars) =
            # # of examples with this assignment of the given vars that have required_var = val / total # of examples with this assignment of the given vars
            if (num_examples != 0):
                prob = num_each_value[val] / num_examples
            else:
                prob = "-"

            new_factor.add_value_at_assignment(prob, [val] + assignments[index])

    #note: this is already normalized.
    return new_factor

def create_variable_factor (var_list, dataset):
    '''
    Given a list variables, and a dataset.

    this function will create a probability factor that is a table of values for
    P(var1, var2, ...)
    using the dataset to compute this probability.
    '''

    new_factor = Factor("new_factor", var_list)

    assignments = list(new_factor.get_assignment_iterator())

    examples_with_assignment = [ [] for i in range(len(assignments))]
    for example in dataset:

        #Determine which assignment of the variables this example corresponds to.
        this_assignment = []
        for var in var_list:
            this_assignment.append( example[int(var.name[0])] )

        #the index of this assignment in the list of assignments.
        index = assignments.index(this_assignment)
        examples_with_assignment[index].append(example)

    for index in range(len(assignments)):

        #P(this assignment) = # of examples with this assignment / total.
        prob = len(examples_with_assignment[index]) / len(dataset)

        new_factor.add_value_at_assignment(prob, assignments[index])

    #note: this is already normalized.
    return new_factor


def print_conditional_factor(fact):
    #fact is a conditional probability factor table.
    scope = fact.get_scope()
    bckwds_fact = Factor(fact.name, scope[1:] + [scope[0]])

    #backwds_fact is fact, but with the variables in a different order.

    #this is done so that first all outputs with Malignant = 2 are printed, then all outputs with malignant = 4.
    #this makes things easier to read.

    for bckwds_assignment in bckwds_fact.get_assignment_iterator():
        #print(assignment)

        out_str = "P(Class == " + str(bckwds_assignment[-1]) + "| "
        given_vars = fact.get_scope()
        given_vars = given_vars[1:]
        cntr = 0
        for var in given_vars:
            out_str += var.name[2:] + ' = ' + str(bckwds_assignment[cntr]) + ', '
            cntr += 1

        #print(bckwds_assignment)
        assignment = [bckwds_assignment[-1]] + bckwds_assignment[0:-1]
        #print(assignment)
        out_str += ") = {}".format(fact.get_value(assignment))
        print(out_str)

def print_variable_factor(fact):
    #fact is a factor table (that isn't conditional probability)
    scope = fact.get_scope()

    for assignment in fact.get_assignment_iterator():
        out_str = "P("
        given_vars = fact.get_scope()
        cntr = 0
        for var in given_vars:
            out_str += var.name[2:] + ' = ' + str(assignment[cntr]) + ', '
            cntr += 1

        #print(assignment)
        out_str += ") = {}".format(fact.get_value(assignment))
        print(out_str)



def output_to_txt(fact):
    '''
    fact is a factor that must be P(malignant | 1 variable)
    This function creates a file containing the data in the factor.
    1st column is value of variable. second column is P(malignant == 4 | variable = value)
    '''
    scope = fact.get_scope()
    filename = scope[1].name[2:] + ".txt"
    output_file = open(filename, 'w')

    for assignment in fact.get_assignment_iterator():
        if assignment[0] == 4:
            to_write = str(assignment[1]) + ',' + str(fact.get_value(assignment)) + '\n'
            output_file.write(to_write)


def check_equal(f1, f2):
    '''
    f1 and f2 are 2 factors.
    They should have the same scope, in the same order. (? I think so, at least?)
    return true if f1 and f2 are equal within an epsilon.
    '''
    are_equal = True
    epsilon = 0.55
    for asssignment in f1.get_assignment_iterator():
        v1 = f1.get_value(asssignment)
        v2 = f2.get_value(asssignment)
        #if there was no data on a certain assignment in a training set,
        # then the value for that assignment is '-' and we ignore it when comparing.
        if v1 != '-' and v2 != '-':

            diff = v1 - v2
            #print(abs(diff))
            if (not (abs(diff) < epsilon)):
                are_equal = False
                break

    return are_equal

def check_independence(fact1, fact2):
    '''
    fact1 is P(malignancy | varA)
    fact2 is P(malignancy | varA, varB)

    Does fact1 == fact2?
    If you assume fact1 == fact2, what error do you get?

    if P(M|A) = P(M|A,B) then:

    -------
    R, B are cond. indep. given Y iff
    P(R, B | Y ) = P(R | Y) * P (B | Y)
    this is equivalent to:
    P(R | B, Y) = P(R |Y)

    ----------
    M, B are cond. indep. given A iff
    P(M | B, A) = P(M |A)
    P(M, B | A ) = P(M | A) * P (B | A)
    ----------
    if Pr(B| A^C) = Pr(B|A) then B is conditionally independent of C given A.
    if Pr(M| A, B) = Pr(M|A) then M is cond. indep of B given A.
    --------
    To determine if fact1 == fact2, I have 2 options:

    1.  write function that calculates P(A, B | C)
        then I can calculate P(M, B | A), and multiply P(M | A) by P(B | A) and check if they are equal (within some epsilon)
        if so, M, B are indep given A.

    2.  For all B = b, check if P(M | B = b, A) = P(M | A), cause if so they are cond indep.

    if cond indep return true.
    '''
    f1_scope = set(fact1.get_scope())
    f2_scope = set(fact2.get_scope())

    vars_to_check = list(f2_scope.difference(f1_scope))
    #vars to check is a list of variables in f2 but not f1.
    var = vars_to_check[0]

    are_equal = True

    for val in var.domain():
        restricted_f2 = restrict_factor(fact2, var, val)
        #print("factor 1:")
        #print_factor(fact1)
        #print("With " + var.name[2:] + " restricted to " + str(val) + ":\n")
        #print_factor(restricted_f2)
        if(not check_equal(restricted_f2, fact1)):
            are_equal = False
            break

    return are_equal


'''
 #  Attribute                     Domain
   -- -----------------------------------------
   1. Sample code number            id number
   2. Clump Thickness               1 - 10
   3. Uniformity of Cell Size       1 - 10
   4. Uniformity of Cell Shape      1 - 10
   5. Marginal Adhesion             1 - 10
   6. Single Epithelial Cell Size   1 - 10
   7. Bare Nuclei                   1 - 10
   8. Bland Chromatin               1 - 10
   9. Normal Nucleoli               1 - 10
  10. Mitoses                       1 - 10
  11. Class:                        (2 for benign, 4 for malignant)

 given: A bayes net, and values for attribute 1 - 10, need to find P(Class = 2) and P(Class = 4)

'''

#initializing all of the variables in the bayes net. The name of the variable is its index in the csv file.
dom = [1,2,3,4,5,6,7,8,9,10]
names = ["Clump Thickness", "Uniformity of Cell Size", "Uniformity of Cell Shape", "Marginal Adhesion","Single Epithelial Cell Size", "Bare Nuclei", "Bland Chromatin", "Normal Nucleoli", "Mitoses", "Class"]

var_list = [0 for i in range(len(names))]

for i in range(len(names)):
    if i == len(names) - 1:
        var_list[i] = Variable("{}_{}".format(i, names[i]), [2,4])
    else:
        var_list[i] = Variable("{}_{}".format(i, names[i]), dom)

#a variables name is index_name, where index is the index of that variable in the csv file.
#note that sample code number isn't included in var_list.

data_file = open("data.txt", 'r')
training_data = []
for line in data_file:
    #separate line from csv file by comma
    split_line = line.split(',')
    #ignore all elements with an unknown value.
    if '?' not in line:
        #covert all elements to integers
        for i in range(len(split_line)):
            split_line[i] = int(split_line[i])
        training_data.append(split_line[1:])

'''
#fact = createFactor(var_list[-1], [var_list[0], var_list[1]], training_data)
fact = createFactor(var_list[-1], [var_list[1]], training_data)
print(fact)
print(fact.get_scope())
print_factor(fact)
'''


'''
#generate a list of factors, P(Malignant | Var) for all variables
factor_list = []
for var in var_list:
    if var != var_list[-1]:
        factor_list.append(createFactor(var_list[-1], [var], training_data))
        output_to_txt(factor_list[-1])
'''

'''
#check for conditional independence for all possible variable combinations.
for var1 in var_list:
    for var2 in var_list:
        if var1 != var_list[-1] and var2 != var_list[-1] and var1 != var2:
            #fact1 is P(malignancy | varA). fact2 is P(malignancy | varA, varB)
            fact1 = createFactor(var_list[-1], [var1], training_data)
            fact2 = createFactor(var_list[-1], [var1, var2], training_data)
            indep = check_independence(fact1, fact2)
            if indep:
                #if Pr(M| A, B) = Pr(M|A) then M is cond. indep of B given A.
                print("malignancy is conditionally independent of " + var2.name[2:] + " given " + var1.name[2:])
            else:
                print("no independence found for these variables")
'''

# if epsilon = 0.55, then
# malignancy is conditionally independent of Uniformity of Cell Shape given Uniformity of Cell Size
#but no other conditional independence with smaller epsilon.

#fact1 = P(Malignant | Clump_thickness)
fact1 = create_conditional_factor(var_list[-1], [var_list[0]], training_data)

#fact2 is P(Malignant | Clump Thickness, Uniformity of Cell Size)
fact2 = create_conditional_factor(var_list[-1], [var_list[0], var_list[1]], training_data)
#print_factor(fact1)
#print_factor(fact2)


#print(check_independence(fact1, fact2))
prob_var = create_variable_factor([var_list[1], var_list[-1]], training_data)
print_variable_factor(prob_var)







