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
import baselines


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



def process_SS_file(path_file_SS):
    """
    Process the similarity file and returns a dictionary with the similarity values for each pair of ebtities.
    :param path_file_SS: similarity file path. The format of each line of the similarity file is "Ent1  Ent2    Sim_SA1 Sim_SA2 Sim_SA3 ... Sim_SAn";
    :return: dict_SS is a dictionary where the keys are tuples of 2 entities and the values are the similarity values taking in consideration different semantic aspects.
    """
    file_SS = open(path_file_SS, 'r')
    dict_SS = {}

    for line in file_SS:
        line = line[:-1]
        split1 = line.split('\t')

        ent1 = split1[0].split('/')[-1]
        ent2 = split1[1].split('/')[-1]
        SS = split1[2:]
        SS_floats = [float(i) for i in SS]
        dict_SS[(ent1, ent2)] = SS_floats

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
        split1 = line.split('\t')
        ent1, ent2 = split1[0], split1[1]
        proxy = float(split1[2][:-1])
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



def run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset_name, path_results, n_partition, path_partition, SSM, aspects, run_baselines = False):
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
    :param run_baselines: boolean. True for running the baselines and False otherwise. The default value is False;
    """
    list_ents, list_ss, list_ss_baselines, list_labels = read_SS_dataset_file(path_file_SS, path_dataset_file)

    if run_baselines:
        aspects_baselines = aspects + ["Avg", "Max"]
        dict_baselines = {}
        for aspect in aspects_baselines:
            dict_baselines[aspect] = []
    
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

        if run_baselines:
            #############  MANUAL SELECTION BASELINES
            print('*******************')
            print('MANUAL SELECTION BASELINES .....')
            print('*******************')
            start_manualselection = time.time()
           
            corr_baselines = baselines.performance_baselines(list_ss_baselines, list_labels, aspects_baselines)
            for i in range(len(aspects_baselines)):
                dict_baselines[aspects_baselines[i]].append(corr_baselines[i])
                
            end_manualselection = time.time()
            print('Execution Time: ' + str(end_manualselection - start_manualselection))
            #############  END BASELINES

        #############  MACHINE LEARNING
        print('*******************')
        print('MACHINE LEARNING .....')
        print('*******************')
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
    
    if run_baselines:
        file_results_withoutML = open(path_results + '/' + SSM + "/ResultsBaselinesWithoutML.txt" , 'a')
        for i in range(len(aspects_baselines)):
            print('*******************')
            print("Median Baseline  "+ str(aspects_baselines[i]))
            print('*******************')
            print(str(dict_baselines[aspects_baselines[i]]))
            print(str(median(dict_baselines[aspects_baselines[i]])))
            file_results_withoutML.write(str(aspects_baselines[i]) + '\t' + str(median(dict_baselines[aspects_baselines[i]])) + '\n')
        file_results_withoutML.close()

    file_results_ML = open(path_results + '/' + SSM + "/ResultsML.txt" , 'a')
    print('*******************')

    for algorithm in algorithms:
        print("Median " + algorithm + ": " )
        print('*******************')
        corrs = dict_ML[algorithm]
        print(str(median(corrs)))
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
    n_arguments = len(sys.argv)
    if n_arguments < 3:

        if n_arguments==2:
            if sys.argv[1] == 'False':
                run_baselines = False
            else:
                run_baselines = True

        if n_arguments==1:
            run_baselines = True

        ########################################################PPI datasets
        n_partition = 10
        aspects = ["biological_process","cellular_component", "molecular_function"]
        embSSMs = ['TransE', 'rdf2vec_skip-gram_wl', 'distMult']
        SSMs = ["ResnikMax_ICSeco", "ResnikBMA_ICSeco", "simGIC_ICSeco"]
        algorithms = ['GP', 'LR', 'XGB', 'RF', 'DT', 'KNN','BR', 'MLP']

        datasets = ['PPI_ALL1', 'PPI_ALL3', 'PPI_DM1', 'PPI_DM3', 'PPI_HS1', 'PPI_HS3', 'PPI_SC1', 'PPI_SC3', 'PPI_EC1', 'PPI_EC3']
        proxies = ['SEQ', 'PPI']
        for proxy in proxies:
            for dataset in datasets:
                path_results = 'Regression/Results/' + dataset + '/' + proxy
                path_partition ='Regression/Results/' + dataset + '/Indexes__crossvalidationTest__Run'
                path_dataset_file = 'Data/kgsimDatasets/' + dataset + '/' + proxy + '/' + dataset + '.txt'
                
                for model_embedding in embSSMs:
                    SSM = 'Embeddings_' + model_embedding
                    path_file_SS = 'SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/embedss_200_'+ model_embedding + '_' + dataset + '.txt'
                    run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)
                    gc.collect()

                for SSM in SSMs:
                    path_file_SS = 'SS_Calculation/SS_files/' + dataset + '/ss_'+ SSM + '_' + dataset + '.txt'
                    run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)
                    gc.collect()

        datasets = ['MF_ALL1', 'MF_ALL3', 'MF_DM1', 'MF_DM3', 'MF_HS1', 'MF_HS3', 'MF_SC1', 'MF_SC3', 'MF_EC1', 'MF_EC3']
        proxies = ['SEQ', 'PFAM']
        for proxy in proxies:
            for dataset in datasets:
                path_results = 'Regression/Results/' + dataset + '/' + proxy
                path_partition ='Regression/Results/' + dataset + '/Indexes__crossvalidationTest__Run'
                path_dataset_file = 'Data/kgsimDatasets/' + dataset + '/' + proxy + '/' + dataset + '.txt'
                
                for model_embedding in embSSMs:
                    SSM = 'Embeddings_' + model_embedding
                    path_file_SS = 'SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/embedss_200_'+ model_embedding + '_' + dataset + '.txt'
                    run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)
                    gc.collect()

                for SSM in SSMs:
                    path_file_SS = 'SS_Calculation/SS_files/' + dataset + '/ss_'+ SSM + '_' + dataset + '.txt'
                    run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)
                    gc.collect()


        ########################################################HPO datasets
        n_partition = 10
        aspects = ["HPO", "biological_process","cellular_component", "molecular_function"]
        embSSMs = ['TransE', 'rdf2vec_skip-gram_wl', 'distMult']
        SSMs = ["ResnikMax_ICSeco", "ResnikBMA_ICSeco", "simGIC_ICSeco"]
        algorithms = ['GP', 'LR', 'XGB', 'RF', 'DT', 'KNN','BR', 'MLP']  

        datasets = ['HPO_dataset']
        proxies = ['PhenSeries']
        for proxy in proxies:
            for dataset in datasets:
                path_results = 'Regression/Results/' + dataset + '/' + proxy
                path_partition ='Regression/Results/' + dataset + '/Indexes__crossvalidationTest__Run'
                path_dataset_file = 'Data/kgsimDatasets/' + dataset + '/' + proxy + '/' + dataset + '_HPOids.txt'
                
                for model_embedding in embSSMs:
                    SSM = 'Embeddings_' + model_embedding
                    path_file_SS = 'SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/embedss_200_'+ model_embedding + '_' + dataset + '.txt'
                    run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)
                    gc.collect()

                for SSM in SSMs:
                    path_file_SS = 'SS_Calculation/SS_files/' + dataset + '/ss_'+ SSM + '_' + dataset + '.txt'
                    run_cross_validation(algorithms, proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)
                    gc.collect()

    else:

        dataset = sys.argv[1]
        SSM = sys.argv[2]
        proxy = sys.argv[3]
        path_dataset_file = sys.argv[4]
        path_file_SS = sys.argv[5]
        n_partition = int(sys.argv[6])
        path_partition = sys.argv[7]
        path_results = sys.argv[8]
        algorithm = sys.argv[9]
        n_aspects = int(sys.argv[10])

        aspects = []
        for i in range(n_aspects):
            aspect = sys.argv[11 + i]
            aspects.append(aspect)

        if sys.argv[-1] == 'False':
            run_baselines = False
        else:
            run_baselines = True

        run_cross_validation([algorithm], proxy, path_file_SS, path_dataset_file, dataset, path_results, n_partition, path_partition, SSM, aspects, run_baselines)

        


