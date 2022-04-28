from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
from statistics import mean, median
import numpy as np
import time
import sys
import copy
import gc
import os
from scipy.stats import pearsonr

from run_withPartitions import *

sys.path.append(os.getcwd()) #add the env path
from config import ALGORITHM, RESULTS_PATH, PATH_PARTITIONS, N_PARTITONS, PROXY, DATASET_FILE, DATASET_NAME, SS_MEASURE, PATH_SA_FILE, PATH_SS_FILE

def performance_baselines(list_SS, list_proxy, aspects):
    """
    Compute the correlation for the static baselines.
    :param list_SS: list of lists. Each list represents an entity pair and its elements are the static similarity values (one for each static baseline);
    :param list_proxy: list of proxy values for each entity pair of datasets;
    :param aspects: list of static baselines;
    :return: list of pearson correlation coefficient values for each static baseline.
    """
    corrs_baselines = []
    for i in range(len(aspects)):
        SS_baseline = [SS[i] for SS in list_SS]
        corr = pearsonr(SS_baseline, list_proxy)[0]
        corrs_baselines.append(corr)
    return corrs_baselines

def baselines(algorithms, proxy, path_file_SS, path_dataset_file, dataset_name, path_results, n_partition,
                         path_partition, SSM, aspects, run_baselines=False):
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

    aspects_baselines = aspects + ["Avg", "Max"]
    dict_baselines = {}
    for aspect in aspects_baselines:
        dict_baselines[aspect] = []


    n_pairs = len(list_labels)
    for Run in range(1, n_partition + 1):

        file_partition = path_partition + 'Indexes__crossvalidationTest__Run' + str(Run) + '.txt'
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

        start_manualselection = time.time()
        corr_baselines = performance_baselines(list_ss_baselines, list_labels, aspects_baselines)
        for i in range(len(aspects_baselines)):
            dict_baselines[aspects_baselines[i]].append(corr_baselines[i])

        end_manualselection = time.time()
        print('Execution Time: ' + str(end_manualselection - start_manualselection))
        #############  END BASELINES


    print('\n')
    print('###########################')
    print("######   RESULTS    #######")
    print('###########################')

    file_results_withoutML = open(path_results + '/' + SSM + "/ResultsBaselinesWithoutML.txt", 'a')
    for i in range(len(aspects_baselines)):
        print("Median Baseline  " + str(aspects_baselines[i])+ ": " + str(median(dict_baselines[aspects_baselines[i]])))
        file_results_withoutML.write(str(aspects_baselines[i]) + '\t' + str(median(dict_baselines[aspects_baselines[i]])) + '\n')
    file_results_withoutML.close()




#############################
##    Calling Functions    ##
#############################

if __name__ == "__main__":
    semantic_aspects, name_aspects = extract_SAs(PATH_SA_FILE)
    baselines([ALGORITHM], PROXY, PATH_SS_FILE, DATASET_FILE, DATASET_NAME, RESULTS_PATH, N_PARTITONS, PATH_PARTITIONS, SS_MEASURE, name_aspects)

