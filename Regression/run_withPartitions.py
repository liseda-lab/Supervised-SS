from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
from statistics import mean, median
import numpy as np
import time
import sys
import copy
import gc
import os

import ML

sys.path.append(os.getcwd()) #add the env path
from config import ALGORITHM, RESULTS_PATH, PATH_PARTITIONS, N_PARTITONS, PROXY, DATASET_FILE, DATASET_NAME, SS_MEASURE, PATH_SA_FILE, PATH_SS_FILE

#####################
##    Functions    ##
#####################

def ensure_dir(path):
    """
    Check whether the specified path is an existing directory or not. And if is not an existing directory, it creates a new directory.
    :param path: path-like object representing a file system path;
    """
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)


def extract_SAs(path_sa_file):
    semantic_aspects, name_aspects = [], []
    sa_file = open(path_sa_file, "r")
    for line in sa_file:
        sa, name = line[:-1].split("\t")
        semantic_aspects.append(sa)
        name_aspects.append(name)
    sa_file.close()
    return semantic_aspects, name_aspects


def process_SS_file(path_file_SS):
    """
    Process the similarity file and returns a dictionary with the similarity values for each pair of ebtities.
    :param path_file_SS: similarity file path. The format of each line of the similarity file is "Ent1  Ent2    Sim_SA1 Sim_SA2 Sim_SA3 ... Sim_SAn";
    :return: dict_SS is a dictionary where the keys are tuples of 2 entities and the values are the similarity values taking in consideration different semantic aspects.
    """
    file_SS = open(path_file_SS, 'r')
    dict_SS = {}

    for line in file_SS:
        split1 = line[:-1].split('\t')
        ent1 = split1[0].split('/')[-1]
        ent2 = split1[1].split('/')[-1]
        SS = split1[2:]

        dict_SS[(ent1, ent2)] = [float(i) for i in SS]

    file_SS.close()
    return dict_SS



def process_dataset(path_dataset_file):
    """
    Process the dataset file and returns a list with the proxy value for each pair of entities.
    :param path_dataset_file: dataset file path. The format of each line of the dataset file is "Ent1  Ent2    Proxy";
    :return: list_proxies is a list where each element represents a list composed by [(ent1, ent2), proxy].
    """
    dataset = open(path_dataset_file, 'r')
    list_proxies = []
    
    for line in dataset:
        split1 = line[:-1].split('\t')
        ent1, ent2 = split1[0], split1[1]
        proxy = float(split1[2])
        list_proxies.append([(ent1, ent2), proxy])

    dataset.close()
    return list_proxies



def read_SS_dataset_file(path_file_SS, path_dataset_file):
    """
    Process the dataset file and the similarity file.
    :param path_file_SS: similarity file path. The format of each line of the similarity file is "Ent1  Ent2    Sim_SA1 Sim_SA2 Sim_SA3 ... Sim_SAn";
    :param path_dataset_file: dataset file path. The format of each line of the dataset file is "Ent1  Ent2    Proxy";
    :return: returns 4 lists.
    list_ents is a list of entity pairs in the dataset (each element of the list is a list [ent1, ent2]).
    list_SS is also a list of lists with the similarity values for each pair (each element of the list is a list [Sim_SA1,Sim_SA2,Sim_SA3,...,Sim_SAn]).
    list_SS_max_avg is a list of lists with the similarity values for each pair, including the average and the maximum (each element of the list is a list [Sim_SA1,Sim_SA2,Sim_SA3,...,Sim_SAn, Sim_AVG, Sim_MAX]).
    proxies is a list of proxy values for each pair in the dataset.
    """
    list_SS, list_SS_max_avg = [], []
    proxies, list_ents = [], []

    dict_SS = process_SS_file(path_file_SS)
    list_labels = process_dataset(path_dataset_file)

    for (ent1, ent2), proxy in list_labels:

        SS_floats = dict_SS[(ent1, ent2)]
        max_SS = max(SS_floats)
        avg_SS = mean(SS_floats)

        list_ents.append([ent1, ent2])
        list_SS.append(SS_floats)
        proxies.append(proxy)

        new_SS_floats = copy.deepcopy(SS_floats)
        new_SS_floats.append(avg_SS)
        new_SS_floats.append(max_SS)
        list_SS_max_avg.append(new_SS_floats)

    return list_ents, list_SS , list_SS_max_avg, proxies



def process_indexes_partition(file_partition):
    """
    Process the partition file and returns a list of indexes.
    :param file_partition: partition file path (each line is a index);
    :return: list of indexes.
    """
    file_partitions = open(file_partition, 'r')
    indexes_partition = []
    for line in file_partitions:
        indexes_partition.append(int(line[:-1]))
    file_partitions.close()
    return indexes_partition



def run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset_name, path_results, n_partition, path_partition, SSM, aspects):
    """
    Run machine learning algorithms to learn the best combination of semantic aspects.
    :param algorithms: list of the algorithm (options:"GP", "LR", "XGB", "RF", "DT", "KNN", "BR", "MLP");
    :param proxy: proxy name (e.g. SEQ, PFAM, PhenSeries, PPI);
    :param path_file_SS: similarity file path. The format of each line of the similarity file is "Ent1  Ent2    Sim_SA1 Sim_SA2 Sim_SA3 ... Sim_SAn";
    :param path_dataset_file: dataset file path. The format of each line of the dataset file is "Ent1  Ent2    Proxy";
    :param dataset_name: name of the dataset;
    :param path_results: path where will be saved the results:
    :param n_partition: number of partitions;
    :param path_partition: the partition files path;
    :param SSM: name of semantic similarity measure;
    :param aspects: list of semantic aspects;
    """
    list_ents, list_ss, list_ss_baselines, list_labels = read_SS_dataset_file(path_file_SS, path_dataset_file)

    dict_ML = {}
    for algorithm in algorithms:
        dict_ML[algorithm] = []
        ensure_dir(path_results  + "/" + SSM + "/" + algorithm + "/")
        file_ML = open(path_results  + "/" + SSM + "/" + algorithm + "/" + "CorrelationResults.txt", 'w')
        file_ML.write('Run' + '\t' + 'Correlation' + '\n')
        file_ML.close()

    n_pairs = len(list_labels)
    for Run in range(1, n_partition + 1):

        file_partition = path_partition + str(Run) + '.txt'
        test_index = process_indexes_partition(file_partition)
        train_index = list(set(range(0, n_pairs)) - set(test_index))
        
        print('###########################')
        print("######   RUN" + str(Run) + "       #######")
        print('###########################')

        list_labels = np.array(list_labels)
        y_train, y_test = list_labels[train_index], list_labels[test_index]
        y_train, y_test = list(y_train), list(y_test)

        list_ss = np.array(list_ss)
        X_train, X_test = list_ss[train_index], list_ss[test_index]
        X_train, X_test = list(X_train), list(X_test)

        print('#########' + SSM + '#########')
        start_ML = time.time()

        for algorithm in algorithms:
            path_output_predictions = path_results  + '/' + SSM + "/" + algorithm + "/Predictions__" + SSM + "__" + dataset_name +  "__Run" + str(Run)

            if algorithm == 'LR':
                filename_Modeloutput = path_results  + '/' + SSM + "/" + algorithm + "/Model__" + SSM + "__" + dataset_name +  "__Run" + str(Run)
                corr = ML.performance_LinearRegression(X_train, X_test, y_train, y_test, path_output_predictions, filename_Modeloutput, aspects)
            if algorithm == 'XGB':
                corr = ML.performance_XGBoost(X_train, X_test, y_train, y_test, path_output_predictions)
            if algorithm == 'DT':
                filename_Modeloutput = path_results  + '/' + SSM + "/" + algorithm + "/Model__" + SSM + "__" + dataset_name +  "__Run" + str(Run)
                corr = ML.performance_DecisionTree(X_train, X_test, y_train, y_test, path_output_predictions, filename_Modeloutput, aspects)
            if algorithm == 'KNN':
                corr = ML.performance_KNN(X_train, X_test, y_train, y_test, path_output_predictions)
            if algorithm == 'BR':
                corr = ML.performance_BayesianRidge(X_train, X_test, y_train, y_test, path_output_predictions)
            if algorithm == 'MLP':
                corr = ML.performance_MLP(X_train, X_test, y_train, y_test, path_output_predictions)
            if algorithm == 'RF':
                corr = ML.performance_RandomForest(X_train, X_test, y_train, y_test, path_output_predictions)
            if algorithm == 'GP':
                filename_model_gp = path_results  + '/' + SSM + "/" + algorithm + "/Model__" + SSM + "__" + dataset_name +  "__Run" + str(Run)
                corr = ML.performance_GP(X_train, X_test, y_train, y_test, path_output_predictions, filename_model_gp)
        
            dict_ML[algorithm].append(corr)

        end_ML = time.time()
        print('Execution Time: ' + str(end_ML - start_ML))
        #############  END MACHINE LEARNING

    print('\n')
    print('###########################')
    print("######   RESULTS    #######")
    print('###########################')
    
    file_results_ML = open(path_results + '/' + SSM + "/ResultsML.txt" , 'a')

    for algorithm in algorithms:
        corrs = dict_ML[algorithm]
        print("Median " + algorithm + ": " + str(median(corrs)))
        file_results_ML.write(algorithm + '\t' + str(median(corrs)) + '\n')
        file_algorithm =open(path_results  + '/' + SSM + "/" + algorithm + "/CorrelationResults.txt", 'a')
        for i in range(len(corrs)):
            file_algorithm.write(str(i+1) + '\t' + str(corrs[i]) + '\n')
        file_algorithm.close()

    file_results_ML.close()
    


#############################
##    Calling Functions    ##
#############################

if __name__ == "__main__":
    semantic_aspects, name_aspects = extract_SAs(PATH_SA_FILE)
    run_cross_validation([ALGORITHM], PROXY, PATH_SS_FILE, DATASET_FILE, DATASET_NAME, RESULTS_PATH, N_PARTITONS, PATH_PARTITIONS, SS_MEASURE, name_aspects)


        


