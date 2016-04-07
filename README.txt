How to run the code:

Run the Predict_Class.py file. This will print the F1 score and the classification rate of a naive Bayes classifier that is trained on 478 examples and verified on 205 examples. 

The naive Bayes used uses only three features to predict the class. (This is the Bayes net that achieved the best performance).
To change the features used in the Bayes net, add or remove elements to the best_vars list. 
Note that var_list[9] should not be added to the list best_vars, since that variable corresponds to the class of the example, and including it will always result in 100% accuracy, since P(A|A) = 1



List of functions:

create_conditional_factor (required_var, given_var_list, dataset):
Creates a factor Pr(required_var | given_var_list) using information from dataset.

create_variable_factor (var_list, dataset):
Creates a factor table representing the joint PDF Pr(var_list) using info from dataset.
var_list could contain just one variable and it will just return P(variable)

print_conditional_factor(fact):
Prints a factor that was created by create_conditional_factor. Used for debugging.

print_variable_factor(fact):
Prints a factor that was created by create_variable_factor. Used for debugging.

output_to_txt(fact):
Output conditional factor to a .txt file. Used to create graphs from data. 

output_joint_distrib_to_txt(fact, filename):
Output a variable factor to a .txt file. Used to create graphs from data. 

check_equal(f1, f2):
Checks if 2 factors are equal within epsilon, return true if they are. 

check_independence(fact1, fact2):
fact1 is P(malignancy | varA). fact2 is P(malignancy | varA, varB)
Checks if M is conditionally independent of B. given A. 

find_correlation(varX, varY, dataset):
Finds correlation between 2 variables. 

naive_bayes_predict(class_var, var_list, training_data, test_data):
Uses a naive bayes net, trained on training_data, to predict the output of all the examples in test_data. Then print the F1 score, and return the classification rate. 
The naive bayes net takes into account only the class variable and the variables in var_list, and assumes that the variables in var_list are all dependent on the class var.
