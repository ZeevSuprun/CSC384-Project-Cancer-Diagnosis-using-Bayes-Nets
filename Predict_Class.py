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
                #no examples available to get data about this value combination, output '-' as probability.
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

        given_vars = fact.get_scope()
        out_str = "P(" + given_vars[0].name[2:] + " == " + str(bckwds_assignment[-1]) + "| "

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
    #fact is a factor table (that isn't a conditional probability)
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

def output_joint_distrib_to_txt(fact, filename):
    '''
    fact is a factor that's a joint distribution of 2 variables.
    This function creates a file containing the data in the factor.
    each column is a value of a variable, the last column is the probability.
    '''
    output_file = open(filename, 'w')

    for assignment in fact.get_assignment_iterator():
            to_write = ""
            for val in assignment:
                to_write += str(val) + ','
            to_write += str(fact.get_value(assignment)) + '\n'
            output_file.write(to_write)



def check_equal(f1, f2):
    '''
    f1 and f2 are 2 factors.
    They should have the same scope, in the same order.
    return true if f1 and f2 are equal within an epsilon.
    '''
    are_equal = True
    epsilon = 0.1
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

    if Pr(M| A, B) = Pr(M|A) then M is cond. indep of B given A.
    This function checks if fact1 == fact2.

    To determine if fact1 == fact2,
    For all B = b, check if P(M | B = b, A) = P(M | A),
    if so, M is conditionally independent of B given A, and return true.

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

        if(not check_equal(restricted_f2, fact1)):
            are_equal = False
            break

    return are_equal

def find_correlation(varX, varY, dataset):
    '''var1 and var2 are variables, dataset is the same thing as before.
    this function returns the correlation between var1 and var2.
    '''
    n = len(dataset) # number of examples

    sum_x = 0
    sum_y = 0
    sum_xy = 0 #sum (x*y)

    sum_x2 = 0 # sum (x^2)
    sum_y2 = 0 # sum (y^2)

    x_index = int(varX.name[0])
    y_index = int(varY.name[0])

    for example in dataset:
        x_i = example[x_index]
        y_i = example[y_index]

        sum_x += x_i
        sum_y += y_i
        sum_xy += x_i * y_i
        sum_x2 += x_i**2
        sum_y2 += y_i**2

    #formula for correlation between x and y.
    corr = (n * sum_xy - sum_x * sum_y) / ((n*sum_x2 - sum_x**2)**0.5 * (n*sum_y2 - sum_y**2)**0.5)
    return corr

def naive_bayes_predict(class_var, var_list, training_data, test_data):
    '''
    class_var is the "class" variable that can take a value of 2 for benign and 4 for malignant.
    var_list is a list of variables (not including the class_var)
    training_data is an array of examples from data.txt to be used for training.
    test_data is another array of examples from data.txt to be used for testing.

    This function prints the F1 score and returns the classification rate on test_data.

    predicted class = argmax over v ( P(Y = v) * Product(P(Xi = ui | Y = v) )
    '''

    prob_class = create_variable_factor([class_var], training_data) #P(Y) factor table.

    #list of P(Xi | Y) for all i
    factor_list = [create_conditional_factor(var, [class_var], training_data) for var in var_list]

    vals_to_assign = [0 for i in range(len(factor_list))]

    num_correct_predictions = 0
    true_pos = 0
    false_pos = 0
    false_neg = 0
    #for every example in the test_data, predict the outcome.
    for example in test_data:
        #populate vals_to_assign using the example
        for i in range(len(vals_to_assign)):
            vals_to_assign[i] = example[int(var_list[i].name[0])]

        prod_2 = prob_class.get_value([2])
        prod_4 = prob_class.get_value([4])

        for i in range(len(factor_list)):
            prod_2 *= factor_list[i].get_value([vals_to_assign[i], 2])
            prod_4 *= factor_list[i].get_value([vals_to_assign[i], 4])

        predicted_result = 0
        if prod_4 > prod_2:
            predicted_result = 4
        else:
            predicted_result = 2

        actual_class = example[int(class_var.name[0])]

        if predicted_result == actual_class:
            num_correct_predictions += 1

        #calculating number of true postives, false positives, false negatives.
        if (predicted_result == 4 and actual_class == 4):
            true_pos += 1
        elif (predicted_result == 4 and actual_class == 2):
            false_pos += 1
        elif (predicted_result == 2 and actual_class == 4):
            false_neg += 1

    #print("number of true positives is {}".format(true_pos))
    #print("number of false positives is {}".format(false_pos))
    #print("number of false negatives is {}".format(false_neg))

    precision = true_pos / (true_pos + false_pos)
    recall = true_pos / (true_pos + false_neg)

    #print("Precision is {}".format(precision))
    #print("Recall is {}".format(recall))

    F1 = 2*precision*recall / (precision + recall)
    print("F1 score is {}".format(F1))
    #return the rate of correct predictions.
    return num_correct_predictions / len(test_data)


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

#a variables name is index_name, where index is the index of that variable in an element of the training_data list.
#note that sample code number isn't included in var_list or in training_data.

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
#training_data is a list of lists. Each element in training_data looks something like this:
#[5, 1, 1, 1, 2, 1, 3, 1, 1, 2]
#where the first value is the value of Clump Thickness, the second element is the value of Uniformity of Cell Size,
#and so on.

'''
#generate a list of factors, P(Malignant | Var) for all variables, and output to a .txt file.
factor_list = []
for var in var_list:
    if var != var_list[-1]:
        factor_list.append(create_conditional_factor(var_list[-1], [var], training_data))
        output_to_txt(factor_list[-1])


#generate a list of joint probability factors, P(Malignant, Var) for all variables, and output to a .txt file.
factor_list = []
for var in var_list:
    if var != var_list[-1]:
        factor_list.append(create_variable_factor([var, var_list[-1]], training_data))
        output_joint_distrib_to_txt(factor_list[-1], "joint_pdf" + str(var_list.index(var)))

#The code in this comment block was used to output files, which were then used to create informative graphs.
'''

'''
#check for conditional independence for all possible variable combinations.
for var1 in var_list:
    for var2 in var_list:
        if var1 != var_list[-1] and var2 != var_list[-1] and var1 != var2:
            #fact1 is P(malignancy | varA). fact2 is P(malignancy | varA, varB)
            fact1 = create_conditional_factor(var_list[-1], [var1], training_data)
            fact2 = create_conditional_factor(var_list[-1], [var1, var2], training_data)
            indep = check_independence(fact1, fact2)
            if indep:
                #if Pr(M| A, B) = Pr(M|A) then M is cond. indep of B given A.
                print("malignancy is conditionally independent of " + var2.name[2:] + " given " + var1.name[2:])
            else:
                print("no independence found for these variables")

#Running the code in this comment block found no conditional independence in the data. This information was used when
#choosing the bayes net structure.
'''

'''
#Printing the correlation matrix
correlation_matrix = [[0.0 for i in var_list] for j in var_list]
print(names)
for i in range(len(var_list)):
    for j in range(i+1):
        corr = find_correlation(var_list[i], var_list[j], training_data)
        correlation_matrix[i][j] = round(corr,2)
    print(correlation_matrix[i])
'''

'''
#Testing to make sure multiplying 2 variables is the same as creating a factor with 2 variables.
#Wait: shouldn't they be equal only if the 2 variables are independent? :?
fact1 = create_variable_factor([var_list[-2]], training_data)
fact2 = create_variable_factor([var_list[-1]], training_data)
fact_join = create_variable_factor([var_list[-2], var_list[-1]], training_data)
mult_fact = multiply_factors([fact1, fact2])

print_variable_factor(fact1)
print_variable_factor(fact2)
print_variable_factor(fact_join)
print_variable_factor(mult_fact)
print(check_equal(fact_join, mult_fact))

#Results: mult_fact and join_fact should be equal.
# It turns out they are equal up to an epsilon of 0.1 for these two variables. (mitosis and class)
'''

#var_list = [0_Clump Thickness, 1_Uniformity of Cell Size, 2_Uniformity of Cell Shape, 3_Marginal Adhesion, 4_Single Epithelial Cell Size, 5_Bare Nuclei, 6_Bland Chromatin, 7_Normal Nucleoli, 8_Mitoses, 9_Class]

n = 478

best_vars = [var_list[1], var_list[4], var_list[6]]
#prediction_rate = naive_bayes_predict(var_list[-1], var_list[0:len(var_list) - 2], training_data[0:n], training_data[n:])
prediction_rate = naive_bayes_predict(var_list[-1], best_vars, training_data[0:n], training_data[n:])
print("Classification rate: {}".format(prediction_rate))

data_file.close()