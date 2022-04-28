import os
import sys
import rdflib
from rdflib.namespace import RDF, OWL, RDFS

import run_embedSS_calculation
import run_OWL2VecEmbeddings
import run_RDF2VecEmbeddings
import run_OpenKEmodel

sys.path.append(os.getcwd()) #add the env path
from config import OS, DATASET_NAME, SPECIES, PROXY, ONTOLOGY, ONTOLOGY_ANNOTATIONS, ONTOLOGY_ANNOTATIONS_FORMAT, NAMESPACE, NAMESPACE_URI, DATASET_FILE, PATH_SS_FILE, SS_MEASURE, PATH_EMBEDDING, PATH_SA_FILE

def ensure_dir(path):
    """
    Check whether the specified path is an existing directory or not. And if is not an existing directory, it creates a new directory.
    :param path: path-like object representing a file system path;
    """
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)



def extract_SAs(path_sa_file):
    semantic_aspects, name_aspects = [], []
    sa_file = open(path_sa_file, "r")
    for line in sa_file:
        sa, name = line[:-1].split("\t")
        semantic_aspects.append(sa)
        name_aspects.append(name)
    sa_file.close()
    return semantic_aspects, name_aspects



def get_taxonomic_measures():
    groupwises_SSMs, pairwises_SSMs = [], []
    ics = ["ICseco", "ICresnik", "ICharispe", "ICsanchez", "ICzhou"]
    groupwises = ["gic", "lee", "deane"]
    pairwises = ["resnik", "li", "pekarstaab", "rada"]
    aggrs = ["max", "bma", "avg", "bmm", "min"]
    for groupwise in groupwises:
        for ic in ics:
            groupwises_SSMs.append(groupwise + '_' + ic)
    for pairwise in pairwises:
        for agg in aggrs:
            for ic in ics:
                pairwises_SSMs.append(pairwise + '_' + agg + '_' + ic)
    return groupwises+pairwises



def run_taxonomic_SS_calculation(os, ontology, ontology_annotations, ontology_annotations_format,  namespace, namespace_uri, dataset_file, path_SS_file, SS_measure, semantic_aspects, name_semantic_aspects):

    str_aspects = ''
    str_name_aspects = ''
    for i in range(len(semantic_aspects)):
        str_aspects = str_aspects + '"' + semantic_aspects[i] + '" '
        name, aspect = name_aspects[i]
        str_name_aspects = str_name_aspects + '"' + name + '" '

    if os == "windows":
        command_1 = 'javac -cp ".;./SS_Calculation/jar_files/*" ./SS_Calculation/Run_SS_calculation_SAs.java'
        os.system(command_1)
        command_2 = 'java -cp ".;./SS_Calculation/jar_files/*" SS_Calculation/Run_SS_calculation_SAs' + ' "' + ontology + '" "' + ontology_annotations + '" "' + namespace + '" "' + namespace_uri + '" "' + ontology_annotations_format + '" "' + dataset_file + '" "' + path_SS_file + '" "' + SS_measure + '" "' + str(len(semantic_aspects)) + '" '
        os.system(command_2 + str_aspects)
    elif os == "linux":
        command_1 = 'javac -cp ".:./SS_Calculation/jar_files/*" ./SS_Calculation/Run_SS_calculation_SAs.java'
        os.system(command_1)
        command_2 = 'java -cp ".:./SS_Calculation/jar_files/*" SS_Calculation/Run_SS_calculation_SAs' + ' "' + ontology + '" "' + ontology_annotations + '" "' + namespace + '" "' + namespace_uri + '" "' + ontology_annotations_format + '" "' + dataset_file + '" "' + path_SS_file + '" "' + SS_measure + '" "' + str(len(semantic_aspects)) + '" '
        os.system(command_2 + str_aspects)



def run_embedding_SS_calculation(ontology, ontology_annotations, ontology_annotations_format, namespace_uri, dataset_file, path_embedding, path_SS_file, SS_measure, semantic_aspects, name_semantic_aspects):

    #### Generating embedding for each semantic aspect
    if SS_measure == "RDF2vec":
        list_embeddings_files = run_RDF2VecEmbeddings.run_embedddings_aspect(ontology, ontology_annotations, ontology_annotations_format, namespace_uri, path_embedding, semantic_aspects, name_semantic_aspects)
    elif SS_measure == "OWL2vec":
        list_embeddings_files = run_OWL2VecEmbeddings.run_embedddings_aspect(ontology, ontology_annotations, ontology_annotations_format, namespace_uri, path_embedding, semantic_aspects, name_semantic_aspects)
    else:
        list_embeddings_files = run_OpenKEmodel.run_embedddings_aspect(ontology, ontology_annotations, ontology_annotations_format, namespace_uri, path_embedding, SS_measure, semantic_aspects, name_semantic_aspects)

    #### Computing embedding-based semantic similarity
    run_embedSS_calculation.process_embedding_files(namespace_uri, dataset_file, list_embeddings_files, path_SS_file)



if __name__ == "__main__":

    semantic_aspects, name_aspects = extract_SAs(PATH_SA_FILE)
    if SS_MEASURE in get_taxonomic_measures():
        run_taxonomic_SS_calculation(OS, ONTOLOGY, ONTOLOGY_ANNOTATIONS, ONTOLOGY_ANNOTATIONS_FORMAT, NAMESPACE, NAMESPACE_URI, DATASET_FILE, PATH_SS_FILE, SS_MEASURE, semantic_aspects, name_aspects)
    elif SS_MEASURE in ["RDF2vec", "OWL2vec", "distMult", "TransE", "TransH", "TransD", "TransR", "ComplEx"]:
        run_embedding_SS_calculation(ONTOLOGY, ONTOLOGY_ANNOTATIONS,ONTOLOGY_ANNOTATIONS_FORMAT, NAMESPACE_URI, DATASET_FILE, PATH_EMBEDDING, PATH_SS_FILE, SS_MEASURE, semantic_aspects, name_aspects)
    else:
        print("SS measure not implemented.")

