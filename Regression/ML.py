import xgboost as xgb
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import BayesianRidge
from sklearn.neural_network import MLPRegressor
from sklearn.utils.validation import check_array
from gplearn.genetic import SymbolicRegressor

import simplificationDTs


#########################
##    GP Parameters    ##
#########################
population_size_value=500
generations_value=50
tournament_size_value=20
stopping_criteria_value=0.0
const_range_value=(-1, 1)
init_depth_value=(2, 6)
init_method_value='half and half'
function_set_value= ['add', 'sub', 'mul', 'max', 'min', 'div']
metric_value='rmse'
parsimony_coefficient_value=0.00001
p_crossover_value=0.9
p_subtree_mutation_value=0.01
p_hoist_mutation_value=0.01
p_point_mutation_value=0.01
p_point_replace_value=0.05
max_samples_value=1.0
warm_start_value=False
n_jobs_value=1
verbose_value=1
random_state_value=None


#####################
##    Functions    ##
#####################

def writePredictions(predictions, y, path_output):
    """
    Write the predictions.
    :param predictions: list of predicted values;
    :param y: list of expected values;
    :param path_output: path of predictions file;
    :return: file with predictions.
    """
    file_predictions = open(path_output, 'w')
    file_predictions.write('Predicted_output' + '\t' + 'Expected_Output' + '\n')
    for i in range(len(y)):
        file_predictions.write(str(predictions[i]) + '\t' + str(y[i]) + '\n')
    file_predictions.close()



def performance_LinearRegression(X_train, X_test, y_train, y_test, path_output_predictions, filename_Modeloutput, aspects):
    """
    Applies Linear Regression Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :param filename_Modeloutput: path of model file;
    :param aspects: list of semantic aspects;
    :return: a predictions file, a model file, and a correlation value on the test set.
    """
    reg_model = LinearRegression().fit(X_train, y_train)
    predictions_train = reg_model.predict(X_train)
    predictions_test = reg_model.predict(X_test)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')
    
    corr_LinearRegression = pearsonr(predictions_test, y_test)[0]
    
    file_model = open(filename_Modeloutput, 'w')
    coefficients = list(reg_model.coef_)
    file_model.write('Aspect' + '\t' + 'Coefficient' + '\n')

    for i in range(len(aspects)):
        file_model.write(aspects[i] + '\t')
        file_model.write(str(coefficients[i]) + '\t')
        file_model.write('\n')

    file_model.write('coefficient' + '\t' + str(reg_model.intercept_) + '\n')
    file_model.write(str())
    file_model.close()
    return corr_LinearRegression



def performance_XGBoost(X_train, X_test, y_train, y_test, path_output_predictions):
    """
    Applies XGBoost Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :return: a predictions file and a correlation value on the test set.
    """
    xgb_model = xgb.XGBRegressor()
    clf = GridSearchCV(xgb_model,
                {'max_depth': [2,4,6],
                 'n_estimators': [50,100,200],
                 'learning_rate': [0.1, 0.01, 0.001]}, verbose=1)
    clf.fit(np.array(X_train), np.array(y_train))

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)

    predictions_test = clf.predict(np.array(X_test))
    predictions_train = clf.predict(np.array(X_train))
    writePredictions(predictions_train.tolist(), y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test.tolist(), y_test, path_output_predictions + '_TestSet')
    
    corr_XGboost = pearsonr(predictions_test, np.array(y_test))[0]
    return corr_XGboost



def performance_RandomForest(X_train, X_test, y_train, y_test, path_output_predictions):
    """
    Applies Random Forest Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :return: a predictions file and a correlation value on the test set.
    """
    rf_model = RandomForestRegressor()
    regressor = GridSearchCV(rf_model,
                {'max_depth': [2,4,6, None],
                 'n_estimators': [50,100,200]})
    regressor.fit(X_train, y_train)

    print("Best parameters set found on development set:")
    print()
    print(regressor.best_params_)
    
    predictions_test = regressor.predict(X_test)
    predictions_train = regressor.predict(X_train)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')

    corr_RandomForest = pearsonr(predictions_test, y_test)[0]
    return corr_RandomForest



def performance_DecisionTree(X_train, X_test, y_train, y_test, path_output_predictions, filename_Modeloutput, aspects, d = None):
    """
    Applies Decision Tree Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :param filename_Modeloutput: path of model file;
    :param aspects: list of semantic aspects;
    :param d: maximum depth of trees (if None there is no maximum depth);
    :return: a predictions file, a model file, and a correlation value on the test set.
    """
    if d == None:
        regressor = DecisionTreeRegressor()
    else:
        regressor = DecisionTreeRegressor(max_depth=d)
    regressor.fit(X_train, y_train)
    
    predictions_test = regressor.predict(X_test)
    predictions_train = regressor.predict(X_train)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')
    
    corr_DecisionTree = pearsonr(predictions_test, y_test)[0]
    
    model = export_text(regressor, aspects)
    with open(filename_Modeloutput, 'w') as file_Modeloutput:
        print(model, file=file_Modeloutput)

    file_rules = open(filename_Modeloutput + "_Simplification", 'w')
    rules_list = simplificationDTs.tree_to_code(regressor, aspects)
    for rule in rules_list:
        file_rules.write( rule + '\n')
    file_rules.close()
    
    return corr_DecisionTree



def performance_SVMregression(X_train, X_test, y_train, y_test, path_output_predictions):
    """
    Applies SVM Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :return: a predictions file and a correlation value on the test set.
    """
    reg_model = SVR()
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
    clf = GridSearchCV(reg_model,tuned_parameters)
    clf.fit(X_train, y_train)

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)

    predictions_test = clf.predict(X_test)
    predictions_train = clf.predict(X_train)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')
    
    corr_SVR = pearsonr(predictions_test, y_test)[0]
    return corr_SVR



def performance_KNN(X_train, X_test, y_train, y_test, path_output_predictions):
    """
    Applies K-Nearest Neighbor Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :return: a predictions file and a correlation value on the test set.
    """
    KNN_model = KNeighborsRegressor()
    KNN_model.fit(X_train, y_train)

    predictions_train = KNN_model.predict(X_train)
    predictions_test = KNN_model.predict(X_test)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')
    
    corr_KNN = pearsonr(predictions_test, y_test)[0]
    return corr_KNN



def performance_BayesianRidge(X_train, X_test, y_train, y_test, path_output_predictions):
    """
    Applies Bayesian Ridge Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :return: a predictions file and a correlation value on the test set.
    """
    Bayesian_model = BayesianRidge()
    Bayesian_model.fit(X_train, y_train)

    predictions_train = Bayesian_model.predict(X_train)
    predictions_test = Bayesian_model.predict(X_test)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')
    
    corr_Bayesian = pearsonr(predictions_test, y_test)[0]
    return corr_Bayesian



def performance_MLP(X_train, X_test, y_train, y_test, path_output_predictions):
    """
    Applies Multi-layer Perceptron Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :return: a predictions file and a correlation value on the test set.
    """
    MLP_regressor = MLPRegressor()
    MLP_regressor.fit(X_train, y_train)
    
    predictions_train = MLP_regressor.predict(X_train)
    predictions_test = MLP_regressor.predict(X_test)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')
    
    corr_MLP = pearsonr(predictions_test, y_test)[0]
    return corr_MLP



def performance_GP(X_train, X_test, y_train, y_test, path_output_predictions, filename_Modeloutput):
    """
    Applies Genetic Programming Algorithm.
    :param X_train: the training input samples. The shape of the list is (n_samplesTrain, n_aspects);
    :param X_test: the testing input samples. The shape of the list is (n_samplesTest, n_aspects);
    :param y_train: the target values (proxy values) of the training set. The shape of the list is (n_samplesTrain);
    :param y_test: the target values (proxy values) of the test set. The shape of the list is (n_samplesTest);
    :param path_output_predictions: path of predictions file;
    :param filename_Modeloutput:  path of model file;
    :return:a predictions file, a model file, and a correlation value on the test set.
    """
    gp = SymbolicRegressor(population_size=population_size_value,
                           generations=generations_value,
                           tournament_size=tournament_size_value,
                           stopping_criteria=stopping_criteria_value,
                           const_range=const_range_value,
                           init_depth=init_depth_value,
                           init_method=init_method_value,
                           function_set=function_set_value,
                           metric=metric_value,
                           parsimony_coefficient=parsimony_coefficient_value,
                           p_crossover=p_crossover_value,
                           p_subtree_mutation=p_subtree_mutation_value,
                           p_hoist_mutation=p_hoist_mutation_value,
                           p_point_mutation=p_point_mutation_value,
                           p_point_replace=p_point_replace_value,
                           max_samples=max_samples_value,
                           warm_start=warm_start_value,
                           n_jobs=n_jobs_value,
                           verbose=verbose_value,
                           random_state=random_state_value)
    gp.fit(X_train, y_train)

    generation = 0
    for program in gp.best_individuals():
        generation = generation + 1

    X_train = check_array(X_train)
    _, gp.n_features = X_train.shape
    predictions_train = program.execute(X_train)
    writePredictions(predictions_train, y_train, path_output_predictions + '_TrainSet')

    X_test = check_array(X_test)
    _, gp.n_features = X_test.shape
    predictions_test = program.execute(X_test)
    writePredictions(predictions_test, y_test, path_output_predictions + '_TestSet')

    file_model = open(filename_Modeloutput, 'w')
    file_model.write(str(gp._program))
    file_model.close()

    corr_GP = pearsonr(predictions_test, y_test)[0]
    return corr_GP



