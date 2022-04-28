import os
import sys
import rdflib
from rdflib.namespace import RDF, OWL, RDFS
import networkx as nx

sys.path.append(os.getcwd()) #add the env path
from config import ONTOLOGY, SA, PATH_SA_FILE


def ensure_dir(path):
    """
    Check whether the specified path is an existing directory or not. And if is not an existing directory, it creates a new directory.
    :param path: path-like object representing a file system path;
    """
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)

def get_semantic_aspects_root(ontology):
    """
    Given an ontology, returns the semantic aspects.
    :param ontology: ontology file path in owl format;
    :return: list with semantic aspects corresponding to the subgraph roots.
    """
    g = rdflib.Graph()
    g.parse(ontology, format='xml')

    non_roots = set()
    roots = set()
    for x, y in g.subject_objects(rdflib.RDFS.subClassOf):
        non_roots.add(x)
        if x in roots:
            roots.remove(x)
        if y not in non_roots:
            if not (isinstance(y, rdflib.term.BNode)):
                roots.add(y)

    aspects = []
    for root in list(roots):
        aspects.append(str(root))

    name_aspects = []
    for aspect in aspects:
        for (sub, pred, obj) in g.triples((rdflib.term.URIRef(aspect), RDFS.label, None)):
            name_aspects.append(str(obj))

    return aspects, name_aspects



def get_semantic_aspects_subroot(ontology):
    """
    Given an ontology, returns the semantic aspects.
    :param ontology: ontology file path in owl format;
    :return: list with semantic aspects corresponding to the subgraph roots.
    """

    g = rdflib.Graph()
    g.parse(ontology, format='xml')

    non_roots = set()
    roots = set()
    for x, y in g.subject_objects(rdflib.RDFS.subClassOf):
        non_roots.add(x)
        if x in roots:
            roots.remove(x)
        if y not in non_roots:
            if not (isinstance(y, rdflib.term.BNode)):
                roots.add(y)

    semantic_aspects = []
    for root in list(roots):
        for (s, p, o) in g.triples((None, rdflib.RDFS.subClassOf, root)):
            if not (isinstance(s, rdflib.term.BNode)):
                semantic_aspects.append(str(s))

    name_aspects = []
    for aspect in semantic_aspects:
        for (sub, pred, obj) in g.triples((rdflib.term.URIRef(aspect), RDFS.label, None)):
            name_aspect = str(obj)
            name_aspects.append((aspect, name_aspect))

    return semantic_aspects, name_aspects

def run_SS_calculation_SAs(ontology, type_aspects, path_file_aspects):

    if type_aspects == "roots":
        semantic_aspects, name_aspects  = get_semantic_aspects_root(ontology)
    if type_aspects == "subroots":
        semantic_aspects, name_aspects  = get_semantic_aspects_subroot(ontology)

    file_aspects = open(path_file_aspects, 'w')
    for i in range(len(name_aspects)):
        file_aspects.write(semantic_aspects[i] + '\t' + name_aspects[i] + '\n')
    file_aspects.close()



if __name__ == "__main__":
    run_SS_calculation_SAs(ONTOLOGY, SA, PATH_SA_FILE)


