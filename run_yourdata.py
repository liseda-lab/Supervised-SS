import os
from SS_Embedding_Calculation.process_KG import get_semantic_aspects

#################
##    Input    ##
#################
"""
:param dataset_name: name of the dataset
:param proxy: proxy name (e.g. SEQ, PFAM, PhenSeries, PPI)
:param ontology: the ontology file path
:param ontology_annotations: annotations file path 
:param ontology_annotations_format: format annotations file path (options are "tsv" or "gaf")
:param namespace: namesapce of the ontology
:param namespace URI
:param dataset_file:  dataset file path with the pairs of entities. The format of each line of the dataset files is "Ent1 Ent2 Proxy"
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
ontology = "Data/GOdata/go-basic.owl"
ontology_annotations = "Data/GOdata/goa_ecoli.gaf"
ontology_annotations_format = "gaf"
namespace = "GO"
namespace_uri = "http://purl.obolibrary.org/obo/GO_"
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



############################
##    Semantic aspects    ##
############################
semantic_aspects = get_semantic_aspects(ontology)
str_aspects = ""
str_name_aspects = ""
for i in range(len(semantic_aspects)):
    str_aspects = str_aspects + '" "' + semantic_aspects[i]
    str_name_aspects = str_name_aspects + '" "SR' + str(i)
str_aspects = str_aspects + '"'
str_name_aspects = str_name_aspects + '"'



#####################################################
##    Taxonomic Semantic Similarity Computation    ##
#####################################################
command_1 = 'javac -cp ".:./SS_Calculation/jar_files/*" ./SS_Calculation/Run_SS_calculation_yourdataset.java'
os.system(command_1)
command_2 = 'java -cp ".:./SS_Calculation/jar_files/*" SS_Calculation/Run_SS_calculation_yourdataset' + ' "' + ontology + '" "' + ontology_annotations + '" "' + namespace + '" "' + namespace_uri + '" "' + ontology_annotations_format + '" "' + dataset_file + '" "' + path_SS_file + '" "' + SS_measure + '" "' + str(
    len(semantic_aspects)) + '" '
os.system(command_2 + str_aspects)



##########################################
##    RDF2Vec Embeddings Computation    ##
##########################################
command_3 = 'python3 SS_Embedding_Calculation/run_RDF2VecEmbeddings.py' + ' "' + size_vector + '" "' + type_walk + '" "' + type_word2vec + '" "' + n_walks + '" "' + dataset_name + '" "' + dataset_file + '" "' + path_embeddings + '" "' + ontology + '" "' + ontology_annotations + '" "' + ontology_annotations_format + '" "' + str(
    len(semantic_aspects))
os.system(command_3 + str_aspects)



#########################################
##    OpenKE Embeddings Computation    ##
#########################################
command_4 = 'python3 SS_Embedding_Calculation/run_OpenKEmodel.py' + ' "' + dataset_name + '" "' + OpenKE_model + '" "' + size_vector + '" "' + path_embeddings + '" "' + dataset_file + '" "' + ontology + '" "' + ontology_annotations + '" "' + ontology_annotations_format + '" "' + str(
    len(semantic_aspects))
os.system(command_4 + str_aspects)



#####################################################
##    Embedding Semantic Similarity Computation    ##
#####################################################
RDF2VecModel = "rdf2vec_" + type_word2vec + "_" + type_walk
ES_rdf2vec_file = path_ES_file + "/embedss_200_" + RDF2VecModel + "_" + dataset_name + ".txt"
str_aspects_emb = ""
for i in range(len(semantic_aspects)):
    file_emb = path_embeddings + "Embeddings_" + dataset_name + "_" + RDF2VecModel + "_SR" + i + ".txt"
    str_aspects_emb = str_aspects_emb + '" "' + file_emb
str_aspects_emb = str_aspects_emb + '"'
command_5 = 'python3 SS_Embedding_Calculation/run_embedSS_calculation.py' + ' "' + dataset_file + '" "' + ES_rdf2vec_file + '" "' + str(
    len(semantic_aspects))
os.system(command_5 + str_aspects_emb)
ES_OpenKE_file = path_ES_file + "/embedss_200_" + OpenKE_model + "_" + dataset_name + ".txt"
str_aspects_emb = ""
for i in range(len(semantic_aspects)):
    file_emb = path_embeddings + "Embeddings_" + dataset_name + "_" + OpenKE_model + "_SR" + i + ".txt"
    str_aspects_emb = str_aspects_emb + '" "' + file_emb
str_aspects_emb = str_aspects_emb + '"'
command_6 = 'python3 SS_Embedding_Calculation/run_embedSS_calculation.py' + ' "' + dataset_file + '" "' + ES_OpenKE_file + '" "' + str(
    len(semantic_aspects))
os.system(command_6 + str_aspects_emb)



##########################################
##    Learning supervised similarity    ##
##########################################
command_7 = 'python3 Regression/run_make_shuffle_partitions.py' + ' "' + dataset_file + '" "' + path_partitions + '" "' + n_partitions + '"'
os.system(command_7)
files_partitions = path_partitions + "Indexes__crossvalidationTest__Run"
SS_file = path_SS_file + "/ss_" + SS_measure + "_" + dataset_name + ".txt"
command_8 = 'python3 Regression/run_withPartitions.py' + ' "' + dataset_name + '" "' + SS_measure + '" "' + proxy + '" "' + dataset_file + '" "' + SS_file + '" "' + n_partitions + '" "' + files_partitions + '" "' + results_path + '" "' + algorithm + '" "' + str(
    len(semantic_aspects)) + str_name_aspects + ' "' + baselines + '"'
os.system(command_8)
command_9 = 'python3 Regression/run_withPartitions.py' + ' "' + dataset_name + '" "' + RDF2VecModel + '" "' + proxy + '" "' + dataset_file + '" "' + ES_rdf2vec_file + '" "' + n_partitions + '" "' + files_partitions + '" "' + results_path + '" "' + algorithm + '" "' + str(
    len(semantic_aspects)) + str_name_aspects + ' "' + baselines + '"'
os.system(command_9)
command_10 = 'python3 Regression/run_withPartitions.py' + ' "' + dataset_name + '" "' + OpenKE_model + '" "' + proxy + '" "' + dataset_file + '" "' + ES_OpenKE_file + '" "' + n_partitions + '" "' + files_partitions + '" "' + results_path + '" "' + algorithm + '" "' + str(
    len(semantic_aspects)) + str_name_aspects + ' "' + baselines + '"'
os.system(command_10)
