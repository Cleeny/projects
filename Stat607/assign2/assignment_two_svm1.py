# Assignment 2, Part 2: Support Vector Machine
#
# Version 0.1

import numpy as np
import kernels as ker
from scipy.optimize import fmin_l_bfgs_b


def svm_train(instances, labels, kernel_func, C=1.0):
    """ Train an SVM using the specified kernel function. """

    n, d = instances.shape

    pm_labels = 2*labels-1  # plus-minus one instead of zero-one

    # TASK 2.1
    # create an n x n kernel matrix
    kernel_mat = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            kernel_mat[i, j] = kernel_func(instances[i],instances[j])

    # TASK 2.2
    # define the dual objective function
    def func(alpha):
        """ The SVM dual objective. """
        alpha_reshaped = np.reshape(alpha,(len(alpha),1))
        labels_reshaped = np.reshape(pm_labels,(len(pm_labels),1))
        x_1 = np.sum(alpha_reshaped)
        x_2 = kernel_mat * np.dot(labels_reshaped, labels_reshaped.T)
        x_3 = np.dot(alpha_reshaped.T, x_2)
        x_4 = np.dot(x_3, alpha_reshaped)
        x_5 = -x_1 + 0.5 * x_4
        return x_5

    # TASK 2.3
    # define the gradient of the dual objective function
    def func_deriv(alpha):
        """ Gradient of the SVM dual objective. """
        alpha_reshaped = np.reshape(alpha,(len(alpha),1))
        labels_reshaped = np.reshape(pm_labels,(len(pm_labels),1))
        x_1 = kernel_mat * np.dot(labels_reshaped, labels_reshaped.T)
        x_2 = np.dot(x_1, alpha_reshaped)
        x_3 = -np.ones((len(alpha),1)) + x_2
        x_4 = np.reshape(x_3, (len(x_3),))
        return x_4

    # TASK 2.4
    # this should be a list containing n pairs (0.0, C)
    box_constraints = [(0.0, C)] * n

    # initial vector for optimization
    alpha0 = np.zeros(n)

    # call the L-BFGS-B method
    alpha, f, d = fmin_l_bfgs_b(func, alpha0, fprime=func_deriv,
                                bounds=box_constraints)

    err_code = d['warnflag']
    if err_code == 0:
        print 'fmin_l_bfgs_b terminated successfully.'
    elif err_code == 1:
        raise Exception('fmin_l_bfgs_b returned error code %d' % err_code)
    elif err_code == 2:
        raise Exception('fmin_l_bfgs_b returned error code %d, reason for \
            error: %s' % (err_code, d['task']))

    alpha_y = alpha * pm_labels

    # TASK 2.5
    # retain only non-zero alpha_y entries
    alpha_y_nz = alpha_y[alpha_y != 0]

    # TASK 2.6
    # retain those instances with non-zero alpha_y entries
    # these are the "support vectors"
    support_vectors = instances[alpha_y != 0]

    num_sv = alpha_y_nz.size  # no. of support vectors

    # TASK 2.7
    # define the svm classifier using kernel_func, support_vectors, and
    # alpha_y_nz
    def classifier(point):
        """ Returns 1 if point is classified as positive, 0 otherwise. """
        a = sum(alpha_y_nz[i] * kernel_func(point, support_vectors[i]) for i in range(num_sv))
        if a > 0:
            return 1
        else:
            return 0
    return classifier


def evaluate_classifier(classifier, instances, labels):
    """ Return a confusion matrix using the given classifier and data set."""

    # TASK 2.8.1
    # extract positive instances, their labels
    positives = instances[labels == 1]
    pos_labels = labels[labels == 1]

    # TASK 2.8.2
    # find the predictions of classifier on positives
    # and count the no. of correct predictions therein
    pos_predictions = np.array([classifier(positives[j,]) for j in range(pos_labels.size)])
    pos_correct = np.sum(np.array(pos_predictions == pos_labels), axis = 0)

    # TASK 2.8.3
    # extract negative instances, their labels
    negatives = instances[labels == 0]
    neg_labels = labels[labels == 0]

    # TASK 2.8.4
    # find the predictions of classifier on negatives
    # and count the no. of correct predictions therein
    neg_predictions = np.array([classifier(negatives[j,]) for j in range(neg_labels.size)])
    neg_correct = np.sum(np.array(neg_predictions == neg_labels), axis = 0)

    confusion_matrix = np.array([[pos_correct, pos_labels.size - pos_correct],
                                 [neg_labels.size - neg_correct, neg_correct]],
                                dtype='float')

    return confusion_matrix


def print_evaluation_summary(confusion_mat):
    """ Print some summary metrics given confusion matrix."""

    TP = confusion_mat[0, 0]
    FN = confusion_mat[0, 1]
    FP = confusion_mat[1, 0]
    TN = confusion_mat[1, 1]

    print "False Positive Rate: %.3f" % (FP/(FP+TN))
    print "False Negative Rate: %.3f" % (FN/(TP+FN))
    print "Recall: %.3f" % (TP/(TP+FN))
    print "Precision: %.3f" % (TP/(TP+FP))
    print "Accuracy: %.3f" % ((TP+TN)/(TP+FN+FP+TN))


def main():

    data_file = 'ionosphere.data'

    data = np.genfromtxt(data_file, delimiter=',', dtype='|S10')
    instances = np.array(data[:, :-1], dtype='float')
    labels = np.array(data[:, -1] == 'g', dtype='int')

    n, d = instances.shape
    nlabels = labels.size

    if n != nlabels:
        raise Exception('Expected same no. of feature vector as no. of labels')

    train_data = instances[:200]  # first 200 examples
    train_labels = labels[:200]  # first 200 labels

    test_data = instances[200:]  # example 201 onwards
    test_labels = labels[200:]  # label 201 onwards

    # parameters for the kernels we'll use
    gamma = 1.0/d
    intercept = 0

    kernel_dict = {'linear': ker.linear,
                   'polynomial': ker.poly(degree=3, gamma=gamma),
                   'rbf/gaussian': ker.rbf(gamma=gamma),
                   'sigmoid/arctan': ker.sigmoid(gamma=gamma)}

    for kernel_name in sorted(kernel_dict.keys()):
        print 'Training an SVM using the %s kernel...' % kernel_name
        svm_classifier = svm_train(train_data, train_labels,
                                   kernel_dict[kernel_name])
        confusion_mat = evaluate_classifier(svm_classifier, test_data,
                                            test_labels)
        print_evaluation_summary(confusion_mat)
        print


if __name__ == '__main__':
    main()
