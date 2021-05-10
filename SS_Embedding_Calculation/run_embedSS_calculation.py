import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys


#####################
##    Functions    ##
#####################

def ensure_dir(path):
    """
    Check whether the specified path is an existing directory or not. And if is not an existing directory, it creates a new directory.
    :param path: A path-like object representing a file system path.
    """
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)



def process_dataset(file_dataset_path):
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

        url_ent1 = "http://" + ent1
        url_ent2 = "http://" + ent2
        
        ents_proxy_list.append([(url_ent1, url_ent2),proxy_value])
    dataset.close()
    return ents_proxy_list



def process_embedding_files(file_dataset_path, list_embeddings_files, output_file):
    """
    Compute cosine similarity between embeddings and write them.
    :param file_dataset_path: dataset file path with the entity pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param list_embeddings_files: list of the embeddings files for each semantic aspect;
    :param output_file: new embedding similarity file path;
    :return: new similarity file;
    """
    ents_proxy_list = process_dataset(file_dataset_path)
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
            ent1 = np.array(dict_embeddings[pair[0]])
            ent1 = ent1.reshape(1,len(ent1))

            ent2 = np.array(dict_embeddings[pair[1]])
            ent2 = ent2.reshape(1,len(ent2))

            sim = cosine_similarity(ent1, ent2)[0][0]
            o.write('\t' + str(sim))

        o.write('\n')
    o.close()



def process_gene_dataset(file_dataset_HPOids, file_dataset_GOids):
    """
    Process the gene dataset file and returns 2 lists with the proxy values for each pair of genes and for each pair of proteins.
    :param file_dataset_HPOids: dataset file path with the pairs of genes;
    :param file_dataset_GOids: dataset file path with the pairs of proteins;
    :return: 2 list of lists. Each list represents a entity pair composed by 2 elements: a tuple (ent1,ent2) and the proxy value;
    """
    dataset_hpo = open(file_dataset_HPOids, 'r')
    dataset_prot = open(file_dataset_GOids, 'r')
    dataset_prot_lines= dataset_prot.readlines()
    genes_proxy_list, prots_proxy_list = [], []

    idx = 0
    for line_hpo in dataset_hpo:
        
        split1_hpo = line_hpo.split('\t')
        gene1, gene2 = split1_hpo[0], split1_hpo[1]
        proxy_hpo = float(split1_hpo[-1][:-1])
        url_gene1 = "http://purl.obolibrary.org/obo/" + gene1
        url_gene2 = "http://purl.obolibrary.org/obo/" + gene2
        genes_proxy_list.append([(url_gene1, url_gene2),proxy_hpo])

        line_prot = dataset_prot_lines[idx]
        split1_prot = line_prot.split('\t')
        prot1, prot2 = split1_prot[0], split1_prot[1]
        proxy_prot = float(split1_prot[-1][:-1])
        url_prot1 = "http://" + prot1
        url_prot2 = "http://" + prot2
        prots_proxy_list.append([(url_prot1, url_prot2),proxy_prot])

        idx = idx + 1

    dataset_hpo.close()
    dataset_prot.close()
    
    return genes_proxy_list, prots_proxy_list



def process_embedding_files_geneDataset(file_dataset_HPOids, file_dataset_GOids, list_embeddings_files_HPO ,list_embeddings_files_GO, output_file):
    """
    Compute cosine similarity between embeddings and write them.
    :param file_dataset_HPOids: dataset file path with the pairs of genes;
    :param file_dataset_GOids: dataset file path with the pairs of proteins;
    :param list_embeddings_files_HPO: list of the embeddings files for HPO;
    :param list_embeddings_files_GO: list of the embeddings files for each GO semantic aspect;
    :param output_file: new embedding similarity file path;
    :return: new similarity file;
    """
    list_labels_genes, list_labels_prots = process_gene_dataset(file_dataset_HPOids, file_dataset_GOids)
    list_dict_HPO = []
    for embedding_file in list_embeddings_files_HPO:
        dict_embeddings= eval(open(embedding_file, 'r').read())
        list_dict_HPO.append(dict_embeddings)

    list_dict_GO = []
    for embedding_file in list_embeddings_files_GO:
        dict_embeddings= eval(open(embedding_file, 'r').read())
        list_dict_GO.append(dict_embeddings)
        
    o=open(output_file,"w")

    i = 0
    for pair_gene, proxy in list_labels_genes:
        gene1=pair_gene[0]
        gene2=pair_gene[1]
        o.write(gene1 + '\t' + gene2)
        pair_prot, proxy  = list_labels_prots[i]

        for dict_embeddings in list_dict_HPO:
            gene1 = np.array(dict_embeddings[pair_gene[0]])
            gene1 = gene1.reshape(1,len(gene1))
            gene2 = np.array(dict_embeddings[pair_gene[1]])
            gene2 = gene2.reshape(1,len(gene2))

            sim = cosine_similarity(gene1, gene2)[0][0]
            o.write('\t' + str(sim))

        for dict_embeddings in list_dict_GO:
            prot1 = np.array(dict_embeddings[pair_prot[0]])
            prot1 = prot1.reshape(1,len(prot1))
            prot2 = np.array(dict_embeddings[pair_prot[1]])
            prot2 = prot2.reshape(1,len(prot2))

            sim = cosine_similarity(prot1, prot2)[0][0]
            o.write('\t' + str(sim))

        o.write('\n')
        i = i+1
        
    o.close()



#############################
##    Calling Functions    ##
#############################

if __name__ == "__main__":

    n_arguments = len(sys.argv)
    if n_arguments == 1:

        model_embeddings = ['rdf2vec_skip-gram_wl', 'TransE', 'distMult']
        n_embeddings = 200
        
        for  model_embedding in  model_embeddings:

            #################### Protein datasets
            datasets = ['MF_ALL1', 'MF_ALL3', 'MF_DM1', 'MF_DM3', 'MF_HS1', 'MF_HS3', 'MF_SC1', 'MF_SC3', 'MF_EC1', 'MF_EC3', 'PPI_ALL1', 'PPI_ALL3', 'PPI_DM1', 'PPI_DM3', 'PPI_HS1', 'PPI_HS3', 'PPI_SC1', 'PPI_SC3', 'PPI_EC1', 'PPI_EC3']
            for dataset in datasets:
                file_dataset_path = 'Data/kgsimDatasets/' + dataset + '/SEQ/' + dataset + '.txt'
                path_embedding_file_bp = 'SS_Embedding_Calculation/Embeddings/' + dataset + '/biological_process/Embeddings_' + dataset + '_'+ model_embedding + '_biological_process.txt'
                path_embedding_file_cc = 'SS_Embedding_Calculation/Embeddings/' + dataset + '/cellular_component/Embeddings_' + dataset + '_'+ model_embedding + '_cellular_component.txt'
                path_embedding_file_mf = 'SS_Embedding_Calculation/Embeddings/' + dataset + '/molecular_function/Embeddings_' + dataset + '_'+ model_embedding + '_molecular_function.txt'
                list_embeddings_files = [path_embedding_file_bp,path_embedding_file_cc,path_embedding_file_mf]
                output_file = 'SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/embedss_'+str(n_embeddings)+'_'+ model_embedding + '_'+dataset+'.txt'

                ensure_dir('SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/')
                process_embedding_files(file_dataset_path, list_embeddings_files ,output_file)

            #################### Gene datasets
            dataset = 'HPO_dataset'
            file_dataset_hpo = 'Data/kgsimDatasets/' + dataset + '/PhenSeries/' + dataset + '_HPOids.txt'
            file_dataset_go = 'Data/kgsimDatasets/' + dataset + '/PhenSeries/' + dataset + '_GOids.txt'
            path_embedding_file_hpo ='SS_Embedding_Calculation/Embeddings/' + dataset + '/HPO/Embeddings_' + dataset + '_'+ model_embedding + '_HPO.txt'
            path_embedding_file_bp = 'SS_Embedding_Calculation/Embeddings/' + dataset + '/biological_process/Embeddings_' + dataset + '_'+ model_embedding + '_biological_process.txt'
            path_embedding_file_cc = 'SS_Embedding_Calculation/Embeddings/' + dataset + '/cellular_component/Embeddings_' + dataset + '_'+ model_embedding + '_cellular_component.txt'
            path_embedding_file_mf = 'SS_Embedding_Calculation/Embeddings/' + dataset + '/molecular_function/Embeddings_' + dataset + '_'+ model_embedding + '_molecular_function.txt'
            list_embeddings_hpo = [path_embedding_file_hpo]
            list_embeddings_go = [path_embedding_file_bp, path_embedding_file_cc, path_embedding_file_mf]
            output_file = 'SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/embedss_'+str(n_embeddings)+'_'+ model_embedding + '_'+dataset+'.txt'

            ensure_dir('SS_Embedding_Calculation/Embeddings_SS_files/' + dataset + '/')
            process_embedding_files_geneDataset(file_dataset_hpo, file_dataset_go, list_embeddings_hpo ,list_embeddings_go, output_file)
            

    else:

        if sys.argv[1] == 'HPOandGO':
            file_dataset_go = sys.argv[2]
            file_dataset_hpo = sys.argv[3]
            output_file = sys.argv[4]
            path_embedding_file_hpo = sys.argv[5]
            list_embeddings_hpo = [path_embedding_file_hpo]
            path_embedding_file_bp = sys.argv[6]
            path_embedding_file_cc = sys.argv[7]
            path_embedding_file_mf = sys.argv[8]
            list_embeddings_go = [path_embedding_file_bp, path_embedding_file_cc, path_embedding_file_mf]

            ensure_dir(output_file)
            process_embedding_files_geneDataset(file_dataset_hpo, file_dataset_go, list_embeddings_hpo ,list_embeddings_go, output_file)

        else:
            file_dataset_path = sys.argv[1]
            output_file = sys.argv[2]
            n_aspects = int(sys.argv[3])
            list_embeddings_files = []
            for i in range(n_aspects):
                path_embedding_file = sys.argv[i + 4]
                list_embeddings_files.append(path_embedding_file)
            
            ensure_dir(output_file)
            process_embedding_files(file_dataset_path, list_embeddings_files ,output_file)

            
        

        
        
