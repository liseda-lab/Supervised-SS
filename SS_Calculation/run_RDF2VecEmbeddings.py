import numpy
import random
import os
from operator import itemgetter

import rdflib
from rdflib.namespace import RDF, OWL, RDFS
import json

from pyrdf2vec.graphs import kg
from pyrdf2vec.rdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec

from pyrdf2vec.samplers import (  # isort: skip
    ObjFreqSampler,
    ObjPredFreqSampler,
    PageRankSampler,
    PredFreqSampler,
    UniformSampler,
    ICSampler,
    PredICSampler,
    RandomSampler,)
from pyrdf2vec.walkers import RandomWalker, WeisfeilerLehmanWalker

import process_KG

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)



########################################################################################################################
###############################################         Parameters        ##############################################
########################################################################################################################

vector_size = 200
n_walks = 100
type_word2vec = "skip-gram"
walk_depth = 4
walker_type = 'wl'
sampler_type = 'uniform'


########################################################################################################################
##############################################      Compute Embeddings      ############################################
########################################################################################################################

def calculate_embeddings(g, ents, path_output, name_embedding, domain):

    graph = kg.rdflib_to_kg(g)

    if type_word2vec == 'CBOW':
        sg_value = 0
    if type_word2vec == 'skip-gram':
        sg_value = 1

    if sampler_type.lower() == 'uniform':
        sampler = UniformSampler()
    elif sampler_type.lower() == 'predfreq':
        sampler = PredFreqSampler()
    elif sampler_type.lower() == 'objfreq':
        sampler = ObjFreqSampler()
    elif sampler_type.lower() == 'objpredfreq':
        sampler = ObjPredFreqSampler()
    elif sampler_type.lower() == 'pagerank':
        sampler = PageRankSampler()
    elif sampler_type.lower() == 'random':
        sampler = RandomSampler()

    if walker_type.lower() == 'random':
        walker = RandomWalker(depth=walk_depth, walks_per_graph=n_walks, sampler = sampler)
    elif walker_type.lower() == 'wl':
        walker = WeisfeilerLehmanWalker(depth=walk_depth, walks_per_graph=n_walks, sampler = sampler)
    elif walker_type.lower() == 'anonymous':
        walker = AnonymousWalker(depth=walk_depth, walks_per_graph=n_walks, sampler = sampler)
    elif walker_type.lower() == 'halk':
        walker = HalkWalker(depth=walk_depth, walks_per_graph=n_walks, sampler = sampler)
    elif walker_type.lower() == 'ngram':
        walker = NGramWalker(depth=walk_depth, walks_per_graph=n_walks, sampler = sampler)
    elif walker_type.lower() == 'walklet':
        walker = WalkletWalker(depth=walk_depth, walks_per_graph=n_walks, sampler = sampler)

    transformer = RDF2VecTransformer(Word2Vec(size=vector_size, sg=sg_value), walkers=[walker])
    embeddings = transformer.fit_transform(graph, ents)
    with open(path_output + 'Embeddings_' + name_embedding + '_' + str(type_word2vec) + '_' + walker_type + '_' +domain + '.txt', 'w') as file:
        file.write("{")
        first = False
        for i in range(len(ents)):
            if first:
                file.write(", '%s':%s" % (str(ents[i]), str(embeddings[i].tolist())))
            else:
                file.write("'%s':%s" % (str(ents[i]), str(embeddings[i].tolist())))
                first = True
            file.flush()
        file.write("}")



########################################################################################################################
##############################################        Call Embeddings       ############################################
########################################################################################################################

def run_embedddings_aspect(ontology_file_path, annotations_file_path, ontology_annotations_format, namespace_uri, path_output, aspects, name_aspects):

    ontology_kg = rdflib.Graph()
    ontology_kg.parse(ontology_file_path, format='xml')

    list_embeddings_files = []
    for i in range(len(aspects)):
        aspect = aspects[i]
        name_aspect = name_aspects[i]
        g, ents  = process_KG.construct_kg_aspect(ontology_kg, annotations_file_path, ontology_annotations_format, aspect, namespace_uri)

        path_output_aspect = path_output + '/' + name_aspect + '/'
        ensure_dir(path_output_aspect)
        list_embeddings_files.append(path_output_aspect + 'Embeddings_rdf2vec_' + str(type_word2vec) + '_' + walker_type + '_' + name_aspect + '.txt')
        
        calculate_embeddings(g, ents, path_output_aspect, "rdf2vec", name_aspect)

    return list_embeddings_files

