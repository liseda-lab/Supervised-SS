import warnings
warnings.filterwarnings("ignore")

import tensorflow as tf
import numpy as np
import os
import json
import rdflib
import sys

from OpenKE import config
from OpenKE import models

from process_KG import *



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



def construct_model(dic_nodes, dic_relations, list_triples, path_output, n_embeddings, models_embeddings, domain):
    """
    Construct and embedding model and compute embeddings.
    :param dic_nodes: dictionary with KG nodes and respective ids;
    :param dic_relations: dictionary with type of relations in the KG and respective ids;
    :param list_triples: list with triples of the KG;
    :param path_output: OpenKE path;
    :param n_embeddings: dimension of embedding vectors;
    :param models_embeddings: list of embedding models;
    :param domain: semantic aspect;
    :return: write a json file with the embeddings for all nodes and relations.
    """
    entity2id_file = open(path_output + "entity2id.txt", "w")
    entity2id_file.write(str(len(dic_nodes))+ '\n')
    for entity , id in dic_nodes.items():
        entity = entity.replace('\n' , ' ')
        entity = entity.replace(' ' , '__' )
        entity = entity.encode('utf8')
        entity2id_file.write(str(entity) + '\t' + str(id)+ '\n')
    entity2id_file.close()

    relations2id_file = open(path_output + "relation2id.txt", "w")
    relations2id_file.write(str(len(dic_relations)) + '\n')
    for relation , id in dic_relations.items():
        relation  = relation.replace('\n' , ' ')
        relation = relation.replace(' ', '__')
        relation = relation.encode('utf8')
        relations2id_file.write(str(relation) + '\t' + str(id) + '\n')
    relations2id_file.close()

    train2id_file = open(path_output + "train2id.txt", "w")
    train2id_file.write(str(len(list_triples)) + '\n')
    for triple in list_triples:
        train2id_file.write(str(triple[0]) + '\t' + str(triple[2]) + '\t' + str(triple[1]) + '\n')
    train2id_file.close()

    # Input training files from data folder.
    con = config.Config()
    con.set_in_path(path_output)
    con.set_dimension(n_embeddings)

    for model_embedding in models_embeddings:
        print('--------------------------------------------------------------------------------------------------------------------')
        print('MODEL: ' + model_embedding)

        # Models will be exported via tf.Saver() automatically.
        con.set_export_files(path_output + model_embedding + "/model_" + species + "_" + domain + ".vec.tf", 0)
        # Model parameters will be exported to json files automatically.
        con.set_out_files(path_output + model_embedding + "/embedding_" + species + "_" + domain + ".vec.json")

        if model_embedding == 'ComplEx':
            con.set_work_threads(8)
            con.set_train_times(1000)
            con.set_nbatches(100)
            con.set_alpha(0.5)
            con.set_lmbda(0.05)
            con.set_bern(1)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("Adagrad")
            # Initialize experimental settings.
            con.init()
            #Set the knowledge embedding model
            con.set_model(models.ComplEx)

        elif model_embedding == 'distMult':
            con.set_work_threads(8)
            con.set_train_times(1000)
            con.set_nbatches(100)
            con.set_alpha(0.5)
            con.set_lmbda(0.05)
            con.set_bern(1)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("Adagrad")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.DistMult)

        elif model_embedding == 'HOLE':
            con.set_work_threads(4)
            con.set_train_times(500)
            con.set_nbatches(100)
            con.set_alpha(0.1)
            con.set_bern(0)
            con.set_margin(0.2)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("Adagrad")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.HolE)

        elif model_embedding == 'RESCAL':
            con.set_work_threads(4)
            con.set_train_times(500)
            con.set_nbatches(100)
            con.set_alpha(0.1)
            con.set_bern(0)
            con.set_margin(1)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("Adagrad")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.RESCAL)

        elif model_embedding == 'TransD':
            con.set_work_threads(8)
            con.set_train_times(1000)
            con.set_nbatches(100)
            con.set_alpha(1.0)
            con.set_margin(4.0)
            con.set_bern(1)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("SGD")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.TransD)

        elif model_embedding == 'TransE':
            con.set_work_threads(8)
            con.set_train_times(1000)
            con.set_nbatches(100)
            con.set_alpha(0.001)
            con.set_margin(1.0)
            con.set_bern(0)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("SGD")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.TransE)

        elif model_embedding == 'TransH':
            con.set_work_threads(8)
            con.set_train_times(1000)
            con.set_nbatches(100)
            con.set_alpha(0.001)
            con.set_margin(1.0)
            con.set_bern(0)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("SGD")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.TransH)

        elif model_embedding == 'TransR':
            con.set_work_threads(8)
            con.set_train_times(1000)
            con.set_nbatches(100)
            con.set_alpha(1.0)
            con.set_lmbda(4.0)
            con.set_margin(1)
            con.set_ent_neg_rate(1)
            con.set_rel_neg_rate(0)
            con.set_opt_method("SGD")
            # Initialize experimental settings.
            con.init()
            # Set the knowledge embedding model
            con.set_model(models.TransR)

        # Train the model.
        con.run()



def write_embeddings(path_model_json, path_embeddings_output, ents, dic_nodes):
    """
    Writing embeddings.
    :param path_model_json: json file with the embeddings for all nodes and relations;
    :param path_embeddings_output: embedding file path;
    :param ents: list of entities for which embeddings will be saved;
    :param dic_nodes: dictionary with KG nodes and respective ids;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}".
    """
    with open(path_model_json, 'r') as embeddings_file:
        data = embeddings_file.read()
    embeddings = json.loads(data)
    embeddings_file.close()

    ensure_dir(path_embeddings_output)
    with open(path_embeddings_output, 'w') as file_output:
        file_output.write("{")
        first = False
        for i in range(len(ents)):
            ent = ents[i]
            if first:
                if "ent_embeddings" in embeddings:
                    file_output.write(", '%s':%s" % (str(ent), str(embeddings["ent_embeddings"][dic_nodes[str(ent)]])))
                else:
                    file_output.write(
                        ", '%s':%s" % (str(ent), str(embeddings["ent_re_embeddings"][dic_nodes[str(ent)]])))
            else:
                if "ent_embeddings" in embeddings:
                    file_output.write("'%s':%s" % (str(ent), str(embeddings["ent_embeddings"][dic_nodes[str(ent)]])))
                else:
                    file_output.write(
                        "'%s':%s" % (str(ent), str(embeddings["ent_re_embeddings"][dic_nodes[str(ent)]])))
                first = True
        file_output.write("}")
    file_output.close()



def construct_embeddings_GO(models_embeddings, n_embeddings, path_output, species, datasets, Graph, domain):
    """
    Calculate embedding using GO KG (GO + GO annotations) and write them on a file.
    :param models_embeddings: list of embedding models;
    :param n_embeddings: dimension of embedding vectors;
    :param path_output: OpenKE path;
    :param species: name of the species;
    :param datasets: list of datasets. Each dataset is a tuple (dataset, file_dataset_path, dataset_output). The "dataset" is the name of the dataset. The "file_dataset_path" is dataset file path with the protein pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy". The "dataset_output" is the embedding files path;
    :param Graph: knowledge graph;
    :param domain: semantic aspect;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}".
    """
    dic_nodes, dic_relations, list_triples = buildIds(Graph)
    construct_model(dic_nodes, dic_relations, list_triples, path_output, n_embeddings, models_embeddings, domain)
    for model_embedding in models_embeddings:
        for dataset, file_dataset_path, dataset_output in datasets:
            dict_labels, prots = process_dataset(file_dataset_path, 'Prot')
            path_model_json = path_output + model_embedding + "/embedding_" + species + "_" + domain + ".vec.json"
            path_embeddings_output = dataset_output + domain + '/' + 'Embeddings_' + str(dataset) + '_' + str(
                model_embedding) + "_" + domain + '.txt'
            write_embeddings(path_model_json, path_embeddings_output, prots, dic_nodes)



def construct_embeddings_HPOwithGO(models_embeddings, n_embeddings, path_output, species, dataset, Graph, domain, ents, dataset_output):
    """
    Calculate embedding using GO KG(GO + GO annotations) and HPO KG (HPO + HPO annotations) and write them on a file.
    :param models_embeddings: list of embedding models;
    :param n_embeddings: dimension of embedding vectors;
    :param path_output: OpenKE path;
    :param species: name of the species;
    :param dataset: name of the dataset;
    :param Graph: knowledge graph;
    :param domain: semantic aspect;
    :param ents: list of entities for which embeddings will be calculated;
    :param dataset_output: embedding files path;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}".
    """
    dic_nodes, dic_relations, list_triples = buildIds(Graph)
    construct_model(dic_nodes, dic_relations, list_triples, path_output, n_embeddings, models_embeddings, domain)
    for model_embedding in models_embeddings:
        path_model_json = path_output + model_embedding + "/embedding_" + species + "_" + domain + ".vec.json"
        path_embeddings_output = dataset_output + domain + '/' + 'Embeddings_' + str(dataset) + '_' + str(model_embedding) + "_" + domain + '.txt'
        write_embeddings(path_model_json, path_embeddings_output, ents, dic_nodes)


def construct_embeddings(model_embedding, n_embeddings, dataset_output, Graph, aspect, dataset_file, dataset):
    """
    Calculate embedding using KG(ontology + annotations) and write them on a file.
    :param model_embedding: embedding model;
    :param n_embeddings: dimension of embedding vectors;
    :param dataset_output: embedding file path;
    :param Graph: knowledge graph;
    :param aspect: semantic aspect;
    :param dataset_file: dataset file path with the entity pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param dataset: name of the dataset;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}".
    """
    path_output = 'SS_Embedding_Calculation/OpenKE/'
    path_model_json = path_output + model_embedding + "/embedding_" + aspect + ".vec.json"
    ensure_dir(dataset_output)
    ensure_dir(path_output + model_embedding)
    path_embeddings_output = dataset_output + '/' + 'Embeddings_' + dataset + '_' + model_embedding + "_" + aspect + '.txt'

    dic_nodes, dic_relations, list_triples = buildIds(Graph)
    construct_model(dic_nodes, dic_relations, list_triples, path_output, n_embeddings, model_embedding, aspect)
    dict_labels, ents = process_dataset(dataset_file)
    write_embeddings(path_model_json, path_embeddings_output, ents, dic_nodes)



def run_model_GO(models_embeddings, n_embeddings, ontology_file_path, annotations_file_path, path_output, species, datasets , domains):
    """
    Calculate embeddings for each semantic aspect using GO KG and write them on a file.
    :param models_embeddings: list of embedding models;
    :param n_embeddings: dimension of embedding vectors;
    :param ontology_file_path: GO ontology file path in owl format;
    :param annotations_file_path: GOA annotations file path in GAF 2.1 version;
    :param path_output: OpenKE path;
    :param species: name of the species;
    :param datasets: list of datasets. Each dataset is a tuple (dataset, file_dataset_path, dataset_output). The "dataset" is the name of the dataset. The "file_dataset_path" is dataset file path with the protein pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy". The "dataset_output" is the embedding files path;
    :param domains: list of GO semantic aspects;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}" for each GO semantic aspect.
    """
    for domain in domains:
        Graph_domain = build_KG_domain_GO(ontology_file_path, annotations_file_path, domain)
        construct_embeddings_GO(models_embeddings, n_embeddings, path_output, species, datasets, Graph_domain, domain)



def run_model_HPO(models_embeddings, n_embeddings, ontology_file_path, annotations_file_path, path_output, species, dataset_name, file_dataset_path, dataset_output, domain):
    """
    Calculate embeddings for each semantic aspect using HPO KG and write them on a file.
    :param models_embeddings: list of embedding models;
    :param n_embeddings: dimension of embedding vectors;
    :param ontology_file_path: HPO ontology file path in owl format;
    :param annotations_file_path: HPO annotations file path in tsv format;
    :param path_output: OpenKE path;
    :param species: name of the species;
    :param dataset_name: name of the dataset;
    :param file_dataset_path: dataset file path with the gene pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param dataset_output: embedding files path;
    :param domain: semantic aspect;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}" for HPO semantic aspect.
    """
    dict_labels, genes = process_dataset(file_dataset_path, 'Gene')
    Graph = buildGraph_HPO(ontology_file_path, annotations_file_path)
    construct_embeddings_HPOwithGO(models_embeddings, n_embeddings, path_output, species, dataset_name, Graph, domain, genes, dataset_output)



def run_model_HPOwithGO(models_embeddings, n_embeddings, ontology_file_path, annotations_file_path, path_output, species, dataset_name, file_dataset_path, dataset_output, domains):
    """
    Calculate embeddings for each semantic aspect using GO KG and write them on a file.
    :param models_embeddings: list of embedding models;
    :param n_embeddings: dimension of embedding vectors;
    :param ontology_file_path: GO ontology file path in owl format;
    :param annotations_file_path: GOA annotations file path in GAF 2.1 version;
    :param path_output: OpenKE path;
    :param species: name of the species;
    :param dataset_name: name of the dataset;
    :param file_dataset_path: dataset file path with the prot pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param dataset_output: embedding files path;
    :param domains: list of GO semantic aspects;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}" for each GO semantic aspect.
    """
    dict_labels, prots = process_dataset(file_dataset_path, 'Prot')
    for domain in domains:
        Graph_domain = build_KG_domain_HPO(ontology_file_path, annotations_file_path, domain, prots)
        construct_embeddings_HPOwithGO(models_embeddings, n_embeddings, path_output, species, dataset_name, Graph_domain, domain, prots, dataset_output)



def run_model_yourdata(dataset_name, model_embedding, n_embeddings, dataset_output, file_dataset_path, ontology_file_path, annotations_file_path, ontology_annotations_format, semantic_aspects):
    """
    Calculate embeddings for each semantic aspect using KG and write them on a file.
    :param dataset_name: name of the dataset;
    :param model_embedding: embedding model;
    :param n_embeddings: dimension of embedding vectors;
    :param dataset_output: embedding file path;
    :param file_dataset_path: dataset file path with the entity pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param ontology_file_path: ontology file path in owl format;
    :param annotations_file_path: annotations file path in GAF 2.1 version;
    :param ontology_annotations_format: format annotations file path (options are "tsv" or "gaf");
    :param semantic_aspects: list with semantic aspects corresponding to the subgraph roots;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}" for each semantic aspect.
    """
    ontology_kg = rdflib.Graph()
    ontology_kg.parse(ontology_file_path, format='xml')
    i = 1
    for aspect in semantic_aspects:
        aspect_name = 'SA' + str(i)
        kg_domain = build_KG_domain(ontology_kg, aspect)
        kg = add_annotations_KG(kg_domain, annotations_file_path, ontology_annotations_format)
        construct_embeddings(model_embedding, n_embeddings, dataset_output, kg, aspect_name, file_dataset_path, dataset_name)
        i = i +1



#############################
##    Calling Functions    ##
#############################

if __name__ == "__main__":

    n_arguments = len(sys.argv)

    if n_arguments == 1:

        models_embeddings = ['distMult', 'TransE']
        
        n_embeddings = 200
        path_output = './SS_Embedding_Calculation/OpenKE/'
        go_file_path = "./Data/GOdata/go-basic.owl"
        hpo_file_path = "./Data/HPOdata/hp.owl"
        HPOannotations_file_path = './Data/HPOdata/annotations_HPO.tsv'
        
        ################ Protein datasets
        domains = ["biological_process", "molecular_function", "cellular_component"]
        annot_files = [("fly", ["MF_DM1", "MF_DM3", "PPI_DM1", "PPI_DM3"]), ( "ecoli", ["MF_EC1", "MF_EC3", "PPI_EC1", "PPI_EC3"]), ("yeast", ["MF_SC1", "MF_SC3", "PPI_SC1", "PPI_SC3"]), ("human", ["MF_HS1", "MF_HS3", "PPI_HS1", "PPI_HS3"]), ("4species" , ["MF_ALL1", "MF_ALL3", "PPI_ALL1", "PPI_ALL3"])]
        
        for species, name_datasets in annot_files:

            annotations_file_path = './Data/GOdata/goa_' + species + '_new.gaf'
            datasets = []
            for dataset in name_datasets:
                file_dataset_path = './Data/kgsimDatasets/' + dataset + '/SEQ/' + dataset + '.txt'
                path_output_embeddings = './SS_Embedding_Calculation/Embeddings/' + dataset + '/'
                datasets.append((dataset , file_dataset_path, path_output_embeddings))
            run_model_GO(models_embeddings, n_embeddings, go_file_path, annotations_file_path, path_output, species, datasets, domains)


        ################ Gene datasets
        dataset_name = 'HPO_dataset'    
        path_output_embeddings = './SS_Embedding_Calculation/Embeddings/' + dataset_name + '/'
        
        species = "hpo_human"
        file_dataset_path = './Data/kgsimDatasets/' + dataset_name + '/PhenSeries/' + dataset_name + '_HPOids.txt'
        domain = "HPO"
        run_model_HPO(models_embeddings, n_embeddings, hpo_file_path, HPOannotations_file_path, path_output, species, dataset_name, file_dataset_path, path_output_embeddings, domain)

        species = "human"
        file_dataset_path = './Data/kgsimDatasets/' + dataset_name + '/PhenSeries/' + dataset_name + '_GOids.txt'
        annotations_file_path = './Data/GOdata/goa_' + species + '_new.gaf'
        domains = ["biological_process", "molecular_function", "cellular_component"]
        run_model_HPOwithGO(models_embeddings, n_embeddings, go_file_path, annotations_file_path, path_output, species, dataset_name, file_dataset_path, path_output_embeddings , domains)

    
    else:

        if sys.argv[1] == 'GO':
            domains = ["biological_process", "molecular_function", "cellular_component"]
            
            path_output = './SS_Embedding_Calculation/OpenKE/'
            n_embeddings = int(sys.argv[2])            
            models_embeddings = [sys.argv[3]]
            dataset_name = sys.argv[4]
            path_output_embeddings = sys.argv[5]
            go_file_path = sys.argv[6]
            annotations_file_path = sys.argv[7]
            species = sys.argv[8]
            file_dataset_path = sys.argv[9]
            
            datasets = [(dataset_name, file_dataset_path,  path_output_embeddings)]
            run_model_GO(models_embeddings, n_embeddings, go_file_path, annotations_file_path, path_output, species, datasets, domains)


        elif sys.argv[1] == 'HPOandGO':

            path_output = './SS_Embedding_Calculation/OpenKE/'

            n_embeddings = int(sys.argv[2])
            models_embeddings = [sys.argv[3]]
            dataset_name = sys.argv[4]
            path_output_embeddings = sys.argv[5]
            go_file_path = sys.argv[6]
            goa_file_path = sys.argv[7]
            species = sys.argv[8]
            file_dataset_path_go = sys.argv[9]
            hpo_file_path = sys.argv[10]
            HPOannotations_file_path = sys.argv[11]
            file_dataset_path_hpo = sys.argv[12]

            domain = "HPO"
            run_model_HPO(models_embeddings, n_embeddings, hpo_file_path, HPOannotations_file_path, path_output, species, dataset_name, file_dataset_path_hpo, path_output_embeddings, domain)

            domains = ["biological_process", "molecular_function", "cellular_component"]
            run_model_HPOwithGO(models_embeddings, n_embeddings, go_file_path, goa_file_path, path_output, species, dataset_name, file_dataset_path_go, path_output_embeddings, domains)


        else:

            dataset_name = sys.argv[1]
            model_embedding = sys.argv[2]
            n_embeddings = int(sys.argv[3])
            dataset_output = sys.argv[4]
            file_dataset_path = sys.argv[5]
            ontology_file_path = sys.argv[6]
            annotations_file_path = sys.argv[7]
            ontology_annotations_format = sys.argv[8]

            semantic_aspects = []
            n_aspects = int(sys.argv[9])
            for i in range(len(n_aspects)):
                aspect = sys.argv[10 + i]
                semantic_aspects.append(aspect)

            run_model_yourdata(dataset_name, model_embedding, n_embeddings, dataset_output, file_dataset_path,
                               ontology_file_path, annotations_file_path, ontology_annotations_format, semantic_aspects)



















