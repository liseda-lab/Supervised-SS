import os

#################
##    Input    ##
#################
"""
:param dataset_name: name of the dataset
:param species: species
:param proxy: proxy name (e.g. SEQ, PFAM, PhenSeries, PPI)
:param GO: the ontology file path
:param GOA: annotations file path in GAF 2.0/2.1 version
:param dataset_file:  dataset file path with the pairs of proteins. The format of each line of the dataset files is "Ent1 Ent2 Proxy"
:param path_SS_file: new SS file path
:param SS_measure: IC-based semantic similarity measures in the format "GroupwiseMeasure_ICmeasure" (e.g., "gic_ICseco") for groupwise measures and in the format "PairwiseMeasure_Aggregation_ICmeasure" (e.g., "resnik_bmm_ICseco") for pairwise measures. 
The available options for ICmeasure are: "ICseco", "ICresnik", "ICharispe", "ICsanchez", "ICzhou". 
The available options for GroupwiseMeasure are: "gic", "lee", "deane". 
The available options for PairwiseMeasure are: "resnik", "li", "pekarstaab", "rada". 
The available options for Aggregation are: "max", "bma", "avg", "bmm", "min". 
For more details, go to https://www.semantic-measures-library.org/sml/index.php?q=sml-semantic-measures.
:param path_embeddings: new embedding files path
:param size_vector: dimension of embedding vectors
:param type_walk: indicate how to construct the sequences fed to the embedder (options are "wl" or "walk") for RDF2Vec
:param type_word2vec: training algorithm (options are "skip-gram" or "CBOW")for RDF2Vec
:param n_walks: maximum number of walks per graph for RDF2Vec
:param OpenKE_model: embedding method (options are "distMult" , "TransE", "TransH", "TransD", "TransR", "ComplEx")
:param path_SS_file: new ES file path
:param n_partitions: number of partitions
:param path_partitions: the partition files path
:param path_results: results path
:param algorithm: name of the algorithm (options:"GP", "LR", "XGB", "RF", "DT", "KNN", "BR", "MLP")
:param baselines: boolean. True for running the baselines and False otherwise. The default value is False
"""
dataset_name = "PPI_EC3"
species = "ecoli"
proxy = "SEQ"
GO = "Data/GOdata/go-basic.owl"
GOA = "Data/GOdata/goa_ecoli.gaf"
dataset_file = "Data/kgsimDatasets/PPI_EC3/SEQ/PPI_EC3.txt"
path_SS_file = "SS_Calculation/SS_files/PPI_EC3"
SS_measure = "gic_ICseco"
path_embeddings = "SS_Embedding_Calculation/Embeddings/PPI_EC3/"
size_vector = "200"
type_walk = "wl"
type_word2vec = "skip-gram"
n_walks = "500"
OpenKE_model = "TransE"
path_ES_file = "SS_Embedding_Calculation/Embeddings_SS_files/PPI_EC3"
n_partitions = "10"
path_partitions = "Regression/Results/PPI_EC3/"
results_path = "Regression/Results/PPI_EC3/SEQ"
algorithm = "LR"
baselines = "True"



#####################################################
##    Taxonomic Semantic Similarity Computation    ##
#####################################################
GOA_new = GOA.split('.gaf')[0] + '_new.gaf'
command_1 = 'javac -cp ".:./SS_Calculation/jar_files/*" ./SS_Calculation/Run_SS_calculation_GO_yourdataset.java'
os.system(command_1)
command_2 = 'java -cp ".:./SS_Calculation/jar_files/*" SS_Calculation/Run_SS_calculation_GO_yourdataset' + ' "' + GO + '" "' + GOA + '" "' + GOA_new + '" "' + dataset_file + '" "' + path_SS_file + '" "' + SS_measure + '"'
os.system(command_2)



##########################################
##    RDF2Vec Embeddings Computation    ##
##########################################
command_3 = 'python3 SS_Embedding_Calculation/run_RDF2VecEmbeddings.py' + ' ' + "GO" + ' "' + size_vector + '" "' + type_walk + '" "' + type_word2vec + '" "' + n_walks + '" "' + dataset_name + '" "' + path_embeddings + '" "' + GO + '" "' + GOA_new + '" "' + dataset_file + '"'
os.system(command_3)



#########################################
##    OpenKE Embeddings Computation    ##
#########################################
command_4 = 'python3 SS_Embedding_Calculation/run_OpenKEmodel.py' + ' ' + "GO" + ' "' + size_vector + '" "' + OpenKE_model + '" "' + dataset_name + '" "' + path_embeddings + '" "' + GO + '" "' + GOA_new + '" "' + species + '" "' + dataset_file + '"'
os.system(command_4)



#####################################################
##    Embedding Semantic Similarity Computation    ##
#####################################################
RDF2VecModel = "rdf2vec_" + type_word2vec + "_" + type_walk
ES_rdf2vec_file = path_ES_file + "/embedss_200_" + RDF2VecModel + "_"+ dataset_name + ".txt"
emb1 = path_embeddings + "biological_process/Embeddings_" + dataset_name + "_" + RDF2VecModel + "_biological_process.txt"
emb2 = path_embeddings + "cellular_component/Embeddings_" + dataset_name + "_" + RDF2VecModel + "_cellular_component.txt"
emb3 = path_embeddings + "molecular_function/Embeddings_" + dataset_name + "_" + RDF2VecModel + "_molecular_function.txt"
command_5 = 'python3 SS_Embedding_Calculation/run_embedSS_calculation.py' + ' "' + dataset_file + '" "' + ES_rdf2vec_file + '" "3" "' + emb1 + '" "' + emb2 + '" "' + emb3 + '"'
os.system(command_5)
ES_OpenKE_file = path_ES_file + "/embedss_200_" + OpenKE_model + "_"+ dataset_name + ".txt"
emb1 = path_embeddings + "biological_process/Embeddings_" + dataset_name + "_" + OpenKE_model + "_biological_process.txt"
emb2 = path_embeddings + "cellular_component/Embeddings_" + dataset_name + "_" + OpenKE_model + "_cellular_component.txt"
emb3 = path_embeddings + "molecular_function/Embeddings_" + dataset_name + "_" + OpenKE_model + "_molecular_function.txt"
command_6 = 'python3 SS_Embedding_Calculation/run_embedSS_calculation.py' + ' "' + dataset_file + '" "' + ES_OpenKE_file + '" "3" "' + emb1 + '" "' + emb2 + '" "' + emb3 + '"'
os.system(command_6)



##########################################
##    Learning supervised similarity    ##
##########################################
command_7 = 'python3 Regression/run_make_shuffle_partitions.py' + ' "' + dataset_file + '" "' + path_partitions + '" "' + n_partitions + '"'
os.system(command_7)
files_partitions = path_partitions + "Indexes__crossvalidationTest__Run"
SS_file = path_SS_file + "/ss_" + SS_measure + "_" + dataset_name + ".txt"
command_8 = 'python3 Regression/run_withPartitions.py' + ' "' + dataset_name + '" "' + SS_measure + '" "' + proxy  + '" "' + dataset_file + '" "' +  SS_file + '" "' + n_partitions + '" "' + files_partitions + '" "' + results_path + '" "' + algorithm + '" "3" "biological_process" "cellular_component" "molecular_function" "' + baselines + '"'
os.system(command_8)
command_9 = 'python3 Regression/run_withPartitions.py' + ' "' + dataset_name + '" "' + RDF2VecModel + '" "' + proxy + '" "' + dataset_file + '" "' + ES_rdf2vec_file + '" "' + n_partitions + '" "' + files_partitions + '" "' + results_path + '" "' + algorithm + '" "3" "biological_process" "cellular_component" "molecular_function" "' + baselines + '"'
os.system(command_9)
command_10 = 'python3 Regression/run_withPartitions.py' + ' "' + dataset_name + '" "' + OpenKE_model + '" "' + proxy + '" "' + dataset_file + '" "' + ES_OpenKE_file + '" "' + n_partitions + '" "' + files_partitions + '" "' + results_path + '" "' + algorithm + '" "3" "biological_process" "cellular_component" "molecular_function" "' + baselines + '"'
os.system(command_10)