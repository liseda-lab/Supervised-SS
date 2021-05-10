import os
import sys

from PyRDF2Vec.graph import *
from PyRDF2Vec.rdf2vec import RDF2VecTransformer

from process_KG import *



##############################
##    RDF2Vec Parameters    ##
##############################
max_path_depth_value=8
max_tree_depth_value=2
window_value=5
n_jobs_value=4
max_iter_value=10
negative_value=25
min_count_value=1
wfl_iterations_value=4



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



def calculate_embeddings(g, ents, path_output, size, type_walk, type_word2vec, n_walks, domain, dataset):
    """
    Calculate embedding and write them on a file.
    :param g: knowledge graph;
    :param ents: list of entities for which embeddings will be calculated;
    :param path_output: embedding file path;
    :param size: dimension of embedding vectors;
    :param type_walk: indicates how to construct the sequences fed to the embedder (options are "wl" or "walk");
    :param type_word2vec: training algorithm (options are "skip-gram" or "CBOW");
    :param n_walks: maximum number of walks per entity;
    :param domain: semantic aspect;
    :param dataset: name of the dataset;
    :return: writes an embedding file with format "{ent1:[...], ent2:[...]}"
    """
    kg = rdflib_to_kg(g)
    graphs_ents = [extract_instance(kg, ent) for ent in ents]

    if type_word2vec == 'CBOW':
        sg_value = 0
    if type_word2vec == 'skip-gram':
        sg_value = 1

    print('----------------------------------------------------------------------------------------')
    print('Computing Embeddings ...')

    transformer = RDF2VecTransformer(vector_size=size,
                                     max_path_depth=max_path_depth_value,
                                     max_tree_depth=max_tree_depth_value,
                                     _type=type_walk,
                                     walks_per_graph=n_walks,
                                     window=window_value,
                                     n_jobs=n_jobs_value,
                                     sg=sg_value,
                                     max_iter=max_iter_value,
                                     negative=negative_value,
                                     min_count=min_count_value,
                                     wfl_iterations=wfl_iterations_value)
    
    embeddings = transformer.fit_transform(graphs_ents)

    # Write embeddings
    print('Writing Embeddings ...')
    ensure_dir(path_output)
    with open(path_output + 'Embeddings_' + dataset +  '_rdf2vec_' + str(type_word2vec) + '_' + str(type_walk) + '_' + domain + '.txt', 'w') as file_embedding:
        file_embedding.write("{")
        first = False
        for i in range(len(ents)):
            if first:
                file_embedding.write(", '%s':%s" % (str(ents[i]), str(embeddings[i].tolist())))
            else:
                file_embedding.write("'%s':%s" % (str(ents[i]), str(embeddings[i].tolist())))
                first=True
                file_embedding.flush()
        file_embedding.write("}")
    print('Finished Embeddings Computation ...')



def run_RDF2Vec_GOembedddings(go_file_path, goa_file_path, list_datasets, vector_size, types_walk, types_word2vec, n_walks, GO_domains):
    """
    Calculate embedding using GO KG (GO + GO annotations) and write them on a file.
    :param go_file_path: GO ontology file path in owl format;
    :param goa_file_path: GOA annotations file path in GAF 2.1 version;
    :param list_datasets: list of datasets. Each dataset is a tuple (dataset_name, path_dataset, path_output_embeddings). The "dataset_name" is the name of the dataset. The "path_dataset" is dataset file path with the protein pairs, the format of each line of the dataset files is "Ent1 Ent2 Proxy". The "path_output_embeddings" is the embedding files path;
    :param vector_size: dimension of embedding vectors;
    :param type_walk: indicates how to construct the sequences fed to the embedder (options are "wl" or "walk");
    :param type_word2vec: training algorithm (options are "skip-gram" or "CBOW");
    :param n_walks: maximum number of walks per entity;
    :param GO_domains: list of semantic aspects (e.g., ["biological_process", "molecular_function", "cellular_component"]);
    :return: writes an embedding file for each semantic aspect with format "{ent1:[...], ent2:[...]}"
    """
    for domain in GO_domains:
        g_domain = build_KG_domain_GO(go_file_path, goa_file_path, domain)
        for dataset_name, path_dataset, path_output_embeddings in list_datasets:
            dict_labels, prots = process_dataset(path_dataset, 'Prot')
            calculate_embeddings(g_domain, prots, path_output_embeddings + domain + '/', vector_size, types_walk, types_word2vec, n_walks, domain, dataset_name)



def run_RDF2Vec_HPOwithGOembedddings(hpo_file_path, HPOannotations_file_path, go_file_path, goa_file_path, vector_sizes, types_walk, types_word2vec, n_walks, path_output_embeddings, path_dataset_hpo, path_dataset_go, dataset_name, GO_domains):
    """
    Calculate embedding using GO KG(GO + GO annotations) and HPO KG (HPO + HPO annotations) and write them on a file.
    :param hpo_file_path: HPO ontology file path in owl format;
    :param HPOannotations_file_path: HPO annotations file path in tsv format;
    :param go_file_path: GO ontology file path in owl format;
    :param goa_file_path: GOA annotations file path in GAF 2.1 version;
    :param vector_sizes: dimension of embedding vectors;
    :param type_walk: indicates how to construct the sequences fed to the embedder (options are "wl" or "walk");
    :param type_word2vec: training algorithm (options are "skip-gram" or "CBOW");
    :param n_walks: maximum number of walks per entity;
    :param path_output_embeddings: embedding files path;
    :param path_dataset_hpo: dataset file path with the correspondent gene pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param path_dataset_go: dataset file path with the protein pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param dataset_name: name of the dataset;
    :param GO_domains: list of semantic aspects (e.g., ["biological_process", "molecular_function", "cellular_component"]);
    :return: writes an embedding file for each semantic aspect with format "{ent1:[...], ent2:[...]}"
    """
    g_hpo = buildGraph_HPO(hpo_file_path, HPOannotations_file_path)
    dict_labels, genes = process_dataset(path_dataset_hpo, 'Gene')
    calculate_embeddings(g_hpo, genes, path_output_embeddings + 'HPO/', vector_sizes, types_walk, types_word2vec, n_walks, 'HPO', dataset_name)

    for domain in GO_domains:
        dict_labels, prots = process_dataset(path_dataset_go, 'Prot')
        g_domain = build_KG_domain_HPO(go_file_path, goa_file_path, domain, prots)
        calculate_embeddings(g_domain, prots, path_output_embeddings + domain + '/', vector_sizes, types_walk, types_word2vec, n_walks, domain, dataset_name)



def run_RDF2VEC_yourdata(dataset_name, size_vector, types_walk, types_word2vec, n_walks, path_embeddings,
                                   dataset_file, ontology, ontology_annotations, ontology_annotations_format,
                                   semantic_aspects):
    ontology_kg = rdflib.Graph()
    ontology_kg.parse(ontology, format='xml')
    dict_labels, ents = process_dataset(dataset_file)

    i = 1
    for aspect in semantic_aspects:
        aspect_name = 'SA' + str(i)
        kg_domain = build_KG_domain(ontology_kg, aspect)
        kg = add_annotations_KG(kg_domain, ontology_annotations, ontology_annotations_format)
        calculate_embeddings(kg, ents, path_embeddings + '/', size_vector, types_walk, types_word2vec, n_walks, aspect,
                             dataset_name)
        i = i + 1



#############################
##    Calling Functions    ##
#############################

if __name__== '__main__':

    n_arguments = len(sys.argv)

    if n_arguments == 1:

        vector_sizes = 200
        n_walks = 500
        types_walk = "wl"
        types_word2vec = "skip-gram"
        hpo_file_path = "Data/HPOdata/hp.owl"
        HPOannotations_file_path = "Data/HPOdata/annotations_HPO.tsv"
        go_file_path = "Data/GOdata/go-basic.owl"
        GO_domains = ["biological_process", "molecular_function", "cellular_component"]

        ################ Protein datasets
        annot_files = [("fly", ["MF_DM1", "MF_DM3", "PPI_DM1", "PPI_DM3"] ), ( "ecoli", ["MF_EC1", "MF_EC3", "PPI_EC1", "PPI_EC3"]), ("yeast", ["MF_SC1", "MF_SC3", "PPI_SC1", "PPI_SC3"]), ("human", ["MF_HS1", "MF_HS3", "PPI_HS1", "PPI_HS3"]), ("4species", ["MF_ALL1", "MF_ALL3", "PPI_ALL1", "PPI_ALL3"])]
        for species, name_datasets in annot_files:
            annotations_file_path = 'Data/GOdata/goa_' + species + '_new.gaf'
            list_datasets = []
            for dataset_name in name_datasets:
                path_dataset = "Data/kgsimDatasets/" + dataset_name + "/SEQ/" + dataset_name + ".txt"
                path_output_embeddings = "SS_Embedding_Calculation/Embeddings/" + dataset_name + "/"
                list_datasets.append((dataset_name, path_dataset, path_output_embeddings))
            run_RDF2Vec_GOembedddings(go_file_path, annotations_file_path, list_datasets, vector_sizes, types_walk, types_word2vec, n_walks, GO_domains)


        ################ Gene datasets
        path_output_embeddings = "SS_Embedding_Calculation/Embeddings/HPO_dataset/"
        path_dataset_hpo = "Data/kgsimDatasets/HPO_dataset/PhenSeries/HPO_dataset_HPOids.txt"
        path_dataset_go = "Data/kgsimDatasets/HPO_dataset/PhenSeries/HPO_dataset_GOids.txt"
        dataset_name = "HPO_dataset"
        goa_file_path = "Data/GOdata/goa_human_new.gaf"
        run_RDF2Vec_HPOwithGOembedddings(hpo_file_path, HPOannotations_file_path, go_file_path, goa_file_path, vector_sizes, types_walk, types_word2vec, n_walks, path_output_embeddings, path_dataset_hpo, path_dataset_go, dataset_name, GO_domains)


    else:
        if sys.argv[1] == 'GO':
            GO_domains = ["biological_process", "molecular_function", "cellular_component"]

            vector_sizes = int(sys.argv[2])
            types_walk = sys.argv[3]
            types_word2vec = sys.argv[4]
            n_walks = int(sys.argv[5])
            dataset_name = sys.argv[6]
            path_output_embeddings = sys.argv[7]
            go_file_path = sys.argv[8]
            annotations_file_path = sys.argv[9]
            file_dataset_path = sys.argv[10]
            list_datasets = [(dataset_name, file_dataset_path,  path_output_embeddings)]

            run_RDF2Vec_GOembedddings(go_file_path, annotations_file_path, list_datasets, vector_sizes, types_walk, types_word2vec, n_walks, GO_domains)


        elif sys.argv[1] == 'HPOandGO':
            GO_domains = ["biological_process", "molecular_function", "cellular_component"]

            vector_sizes = int(sys.argv[2])
            types_walk = sys.argv[3]
            types_word2vec = sys.argv[4]
            n_walks = int(sys.argv[5])
            dataset_name = sys.argv[6]
            path_output_embeddings = sys.argv[7]
            go_file_path = sys.argv[8]
            goa_file_path = sys.argv[9]
            path_dataset_go = sys.argv[10]
            hpo_file_path = sys.argv[11]
            HPOannotations_file_path = sys.argv[12]
            path_dataset_hpo = sys.argv[13]

            run_RDF2Vec_HPOwithGOembedddings(hpo_file_path, HPOannotations_file_path, go_file_path, goa_file_path, vector_sizes, types_walk, types_word2vec, n_walks, path_output_embeddings, path_dataset_hpo, path_dataset_go, dataset_name, GO_domains)


        else:
            size_vector= int(sys.argv[1])
            types_walk = sys.argv[2]
            types_word2vec = sys.argv[3]
            n_walks = int(sys.argv[4])
            dataset_name = sys.argv[5]
            dataset_file = sys.argv[6]
            path_output_embeddings = sys.argv[7]
            ontology = sys.argv[8]
            ontology_annotations = sys.argv[9]
            ontology_annotations_format = sys.argv[10]

            semantic_aspects = []
            n_aspects = int(sys.argv[11])
            for i in range(len(n_aspects)):
                aspect = sys.argv[12 + i]
                semantic_aspects.append(aspect)

            run_RDF2VEC_yourdata(dataset_name, size_vector, types_walk, types_word2vec, n_walks, path_output_embeddings,
                                 dataset_file, ontology, ontology_annotations, ontology_annotations_format,
                                 semantic_aspects)



