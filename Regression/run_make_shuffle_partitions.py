import numpy
import pandas as pd
import os
import sys
from statistics import mean, median
from sklearn.model_selection import KFold

sys.path.append(os.getcwd()) #add the env path
from config import N_PARTITONS, PATH_PARTITIONS, DATASET_FILE

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



def process_dataset_files(file_dataset_path):
    """
    Process the dataset file.
    :param file_dataset_path: dataset file path with the correspondent entity pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :return: list of tuples. Each tuple represents a pair of entities;
    """
    dataset = open(file_dataset_path, 'r')
    ent_pairs = []
    for line in dataset:
        split1 = line.split('\t')
        ent1, ent2 = split1[0], split1[1]
        ent_pairs.append((ent1, ent2))
    dataset.close()
    return ent_pairs



def run_partition(file_dataset_path, filename_output, n_partitions):
    """
    Write partition files with indexes of each test partition.
    :param file_dataset_path: dataset file path with the correspondent entity pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param filename_output: the partition files path;
    :param n_partitions: number of partitions;
    :return: partition files;
    """
    ent_pairs  = process_dataset_files(file_dataset_path)
    skf = KFold(n_splits=n_partitions , shuffle=True)
    ensure_dir(filename_output)

    index_partition = 1
    for indexes_partition_train, indexes_partition_test in skf.split(ent_pairs):
        file_crossValidation_train = open(filename_output + 'Indexes__crossvalidationTrain__Run' + str(index_partition) + '.txt', 'w')
        file_crossValidation_test = open(filename_output + 'Indexes__crossvalidationTest__Run' + str(index_partition) + '.txt', 'w')
        for index in indexes_partition_train:
            file_crossValidation_train.write(str(index) + '\n')
        for index in indexes_partition_test:
            file_crossValidation_test.write(str(index) + '\n')
        file_crossValidation_train.close()
        file_crossValidation_test.close()
        index_partition = index_partition + 1



#############################
##    Calling Functions    ##
#############################

if __name__== '__main__':
    run_partition(DATASET_FILE, PATH_PARTITIONS, N_PARTITONS)



