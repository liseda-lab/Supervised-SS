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
:param sa: str (options:"roots", "subroots", "manual")
:param list_sa: list of urls that is required if sa="manual"
"""

DATASET_NAME = "PPI_EC3"
SPECIES = "ecoli"
PROXY = "SEQ"
ONTOLOGY = "Data/GOdata/go-basic.owl"
ONTOLOGY_ANNOTATIONS = "Data/GOdata/goa_ecoli.gaf"
ONTOLOGY_ANNOTATIONS_FORMAT = "gaf"
NAMESPACE = "GO"
NAMESPACE_URO = "http://purl.obolibrary.org/obo/GO_"
DATASET_FILE = "Data/kgsimDatasets/PPI_EC3/SEQ/PPI_EC3.txt"
PATH_SS_FILE = "SS_Calculation/SS_files/PPI_EC3"
SS_MEASURE = "gic_ICseco"
PATH_EMPEDDING = "SS_Embedding_Calculation/Embeddings/PPI_EC3/"
SIZE_VECTOR = 200
TYPE_WALK = "wl"
TYPE_WORD2VEC = "skip-gram"
N_WALKS = 500
OPENKE_MODEL = "TransE"
PATH_ES_FILE = "SS_Embedding_Calculation/Embeddings_SS_files/PPI_EC3"
N_PARTITONS = 10
PATH_PARTITIONS = "Regression/Results/PPI_EC3/"
RESULTS_PATH = "Regression/Results/PPI_EC3/SEQ"
ALGORITHM = "LR"
BASELINES = True

SA = "roots"
LIST_SA = ["http://purl.obolibrary.org/obo/GO_0008150", "http://purl.obolibrary.org/obo/GO_0005575", "http://purl.obolibrary.org/obo/GO_0003674"]
