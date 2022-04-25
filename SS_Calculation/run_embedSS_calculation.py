import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys



def ensure_dir(path):
    """
    Check whether the specified path is an existing directory or not. And if is not an existing directory, it creates a new directory.
    :param path: A path-like object representing a file system path.
    """
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)



def process_dataset(file_dataset_path, namespace_uri):
    """
    Process the dataset file and returns a list with the proxy values for each pair of entities.
    :param file_dataset_path: dataset file path. The format of each line of the dataset files is "Ent1  Ent2   Proxy";
    :return: a list of lists. Each list represents a entity pair composed by 2 elements: a tuple (ent1,ent2) and the proxy value;
    """

    dataset = open(file_dataset_path, 'r')
    ents_proxy_list = []
    for line in dataset:
        split1 = line.split('\t')
        ent1, ent2 = split1[0], split1[1]
        proxy_value = float(split1[-1][:-1])

        url_ent1 = namespace_uri + ent1
        url_ent2 = namespace_uri + ent2

        ents_proxy_list.append([(url_ent1, url_ent2), proxy_value])
    dataset.close()
    return ents_proxy_list


def process_embedding_files(namespace_uri, file_dataset_path, list_embeddings_files, output_file):
    """
    Compute cosine similarity between embeddings and write them.
    :param file_dataset_path: dataset file path with the entity pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param list_embeddings_files: list of the embeddings files for each semantic aspect;
    :param output_file: new embedding similarity file path;
    :return: new similarity file;
    """

    ents_proxy_list = process_dataset_prots(file_dataset_path, namespace_uri)

    list_dict = []
    for embedding_file in list_embeddings_files:
        dict_embeddings= eval(open(embedding_file, 'r').read())
        list_dict.append(dict_embeddings)
        
    o=open(output_file,"w")
    for pair, label in ents_proxy_list:
        ent1=pair[0]
        ent2=pair[1]
        o.write(ent1+'\t'+ent2)
        
        for dict_embeddings in list_dict:

            if (pair[0] in dict_embeddings) and (pair[1] in dict_embeddings):
                ent1 = np.array(dict_embeddings[pair[0]])
                ent1 = ent1.reshape(1,len(ent1))

                ent2 = np.array(dict_embeddings[pair[1]])
                ent2 = ent2.reshape(1,len(ent2))

                sim = cosine_similarity(ent1, ent2)[0][0]
                o.write('\t' + str(sim))
            else:
                o.write('\t' + str(0))

        o.write('\n')
    o.close()



