import rdflib 
from rdflib.namespace import RDF, OWL



########################################################################################################################
##############################################         Construct KGs        ############################################
########################################################################################################################

def recursive(obj, g_domain, ontology_kg):
    for (s, p, o) in ontology_kg.triples((None, rdflib.RDFS.subClassOf, rdflib.term.URIRef(obj))):
        g_domain.add((s, p, o))
        recursive(s, g_domain, ontology_kg)
    return g_domain


def construct_kg_aspect(ontology_kg, annotations_file_path, ontology_annotations_format, aspect, namespace_uri):

    g_domain = rdflib.Graph()
    g_domain = recursive(aspect, g_domain, ontology_kg)

    file_annot = open(annotations_file_path , 'r')
    file_annot.readline()

    ents = []
    for annot in file_annot:

        if ontology_annotations_format == 'gaf':
            list_annot = annot.split('\t')
            id_ent, ont_term = list_annot[1], list_annot[4]
        if ontology_annotations_format == 'tsv':
            id_ent, ont_term = annot[:-1].split('\t')

        url_ont_term = namespace_uri + ont_term.split(':')[1]
        url_ent =  "http://" + id_ent

        if ((rdflib.term.URIRef(url_ont_term), None, None) in g_domain) or ((None, None, (rdflib.term.URIRef(url_ont_term)))in g_domain):
            g_domain.add((rdflib.term.URIRef(url_ent), rdflib.term.URIRef('http://hasAnnotation') , rdflib.term.URIRef(url_ont_term)))
        else:
            g_domain.add((rdflib.term.URIRef(url_ent), RDF.type, rdflib.BNode()))

        ents.append(url_ent)

    file_annot.close()
    return g_domain, ents



def buildIds(g):
    """
    Assigns ids to KG nodes and KG relations.
    :param g: knowledge graph;
    :return: 2 dictionaries and one list. "dic_nodes" is a dictionary with KG nodes and respective ids. "dic_relations" is a dictionary with type of relations in the KG and respective ids. "list_triples" is a list with triples of the KG.
    """
    dic_nodes = {}
    id_node = 0
    id_relation = 0
    dic_relations = {}
    list_triples = []

    for (subj, predicate , obj) in g:
        if str(subj) not in dic_nodes:
            dic_nodes[str(subj)] = id_node
            id_node = id_node + 1
        if str(obj) not in dic_nodes:
            dic_nodes[str(obj)] = id_node
            id_node = id_node + 1
        if str(predicate) not in dic_relations:
            dic_relations[str(predicate)] = id_relation
            id_relation = id_relation + 1
        list_triples.append([dic_nodes[str(subj)] , dic_relations[str(predicate)] , dic_nodes[str(obj)]])

    return dic_nodes , dic_relations , list_triples
    


