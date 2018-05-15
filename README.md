# CSC384-Project-Cancer-Diagnosis-using-Bayes-Nets

The purpose of this project is to predict whether or not a tumor is cancerous given a data set (found in data.txt) containing information about the tumor. The data set, found in data.txt, contrains data in the following format:
[1041801,5,3,3,3,2,3,4,4,1,4]
where the first number is the sample id, the last is tumor class (2 for benign, 4 for malignant), and 9 values in between are tumor’s characteristics in the following order(from left to right):
1. Clump Thickness
2. Uniformity of Cell Size
3. Uniformity of Cell Shape 4. Marginal Adhesion
5. Single Epithelial Cell Size 6. Bare Nuclei
7. Bland Chromatin
8. Normal Nucleoli
9. Mitoses

A bayes net was used to find the probability that the tumour was cancerous given the other data, using 70% of the data as a training set and 30% of the data as a test set. The best bayes net topology found resulted in 98.5% accuracy. For a more detailed discription of the underlying concepts, see the Project Report. 

The file BayesianNetwork.py contains various classes and helper functions that were used to construct the network. This code was provided by the course instructors.

The file VariableElimination.py contains various helper functions. 

The file predictClass.py contains code that constructs various different bayes nets and uses them to make predictions on the test set using the data from the training set.
