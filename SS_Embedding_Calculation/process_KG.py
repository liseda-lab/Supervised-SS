import rdflib 
from rdflib.namespace import RDF, OWL


#####################
##    Functions    ##
#####################

def get_semantic_aspects(ontology):
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
            name_aspect = str(obj)
            name_aspects.append((aspect, name_aspect))

    return aspects



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

    return semantic_aspects


def _identity(x): return x

def _rdflib_to_networkx_graph(
        graph,
        nxgraph,
        calc_weights,
        edge_attrs,
        transform_s=_identity, transform_o=_identity):
    """Helper method for multidigraph, digraph and graph.
    Modifies nxgraph in-place!
    Arguments:
        graph: an rdflib.Graph.
        nxgraph: a networkx.Graph/DiGraph/MultiDigraph.
        calc_weights: If True adds a 'weight' attribute to each edge according
            to the count of s,p,o triples between s and o, which is meaningful
            for Graph/DiGraph.
        edge_attrs: Callable to construct edge data from s, p, o.
           'triples' attribute is handled specially to be merged.
           'weight' should not be generated if calc_weights==True.
           (see invokers below!)
        transform_s: Callable to transform node generated from s.
        transform_o: Callable to transform node generated from o.
    """
    assert callable(edge_attrs)
    assert callable(transform_s)
    assert callable(transform_o)
    import networkx as nx
    for s, p, o in graph:
        ts, to = transform_s(s), transform_o(o)  # apply possible transformations
        data = nxgraph.get_edge_data(ts, to)
        if data is None or isinstance(nxgraph, nx.MultiDiGraph):
            # no edge yet, set defaults
            data = edge_attrs(s, p, o)
            if calc_weights:
                data['weight'] = 1
            nxgraph.add_edge(ts, to, **data)
        else:
            # already have an edge, just update attributes
            if calc_weights:
                data['weight'] += 1
            if 'triples' in data:
                d = edge_attrs(s, p, o)
                data['triples'].extend(d['triples'])


def add_annotations_KG(kg_domain, ontology_annotations, ontology_annotations_format):
    """
    Adds annotation to KG.
    :param kg_domain: KG (composed by ontology) for a semantic aspect;
    :param ontology_annotations: annotations file path;
    :param ontology_annotations_format: format annotations file path (options are "tsv" or "gaf");
    :return: KG (ontology + annotation) for a semantic aspect.
    """
    file_annot = open(ontology_annotations, 'r')
    for annot in file_annot:

        if ontology_annotations_format == 'gaf':
            list_annot = annot.split('\t')
            ent, ontology_term = list_annot[1], list_annot[4]
        if ontology_annotations_format == 'tsv':
            ent, ontology_term = annot[:-1].split('\t')

        url_ent = "http://" + ent
        if ((rdflib.term.URIRef(ontology_term), None, None) in kg_domain) or ((None, None, (rdflib.term.URIRef(ontology_term)))in kg_domain):
            kg_domain.add((rdflib.term.URIRef(url_ent), rdflib.term.URIRef('http://www.geneontology.org/hasAnnotation') , rdflib.term.URIRef(ontology_term)))
        else:
            kg_domain.add((rdflib.term.URIRef(url_ent), rdflib.namespace.RDF.type, rdflib.BNode()))

    file_annot.close()



def process_dataset(file_dataset_path, type_data="Prot"):
    """
    Process a dataset file.
    :param file_dataset_path: dataset file path with the correspondent entity pairs. The format of each line of the dataset files is "Ent1 Ent2 Proxy";
    :param type_data: options are "Prot" for protein datasets and "Gene" for gene datasets;
    :return: one dictionary and one list. "dict_labels" is a dictionary with entity pairs and respective similarity proxy. "ents" is a list of entities for which embeddings will be computed.
    """
    dataset = open(file_dataset_path, 'r')
    dict_labels = {}
    ents =[]

    for line in dataset:
        split1 = line.split('\t')
        ent1, ent2 = split1[0], split1[1]
        label = float(split1[-1][:-1])

        if type_data == 'Prot':
            url_ent1 = "http://" + ent1
            url_ent2 = "http://" + ent2

        if type_data == 'Gene':
            url_ent1 = "http://purl.obolibrary.org/obo/" + ent1
            url_ent2 = "http://purl.obolibrary.org/obo/" +ent2

        dict_labels[(url_ent1, url_ent2)] = label

        if url_ent1 not in ents:
            ents.append(url_ent1)
        if url_ent2 not in ents:
            ents.append(url_ent2)

    dataset.close()
    return dict_labels, ents



def build_KG_domain_GO(ontology_file_path, annotations_file_path, domain):
    """
    Builds the KG for a GO semantic aspect.
    :param ontology_file_path: GO ontology file path in owl format;
    :param annotations_file_path: GOA annotations file path in GAF 2.1 version;
    :param domain: semantic aspect. Domain can be "molecular_function", "biological_process", "cellular_component";
    :return: a KG for a GO semantic aspect.
    """
    g = rdflib.Graph()
    g_domain = rdflib.Graph()
    # Process ontology file
    g.parse(ontology_file_path, format='xml')

    for (sub, pred, obj) in g.triples((None,None, None)):
        if g.__contains__((sub, rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'), rdflib.term.Literal(domain, datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')))):
            g_domain.add(((sub, pred, obj)))

    file_annot = open(annotations_file_path , 'r')
    file_annot.readline()

    for annot in file_annot:
        list_annot = annot.split('\t')
        id_prot, GO_term = list_annot[1], list_annot[4]

        url_GO_term = "http://purl.obolibrary.org/obo/GO_" + GO_term.split(':')[1]
        url_prot = "http://" + id_prot

        if ((rdflib.term.URIRef(url_GO_term), None, None) in g_domain) or ((None, None, (rdflib.term.URIRef(url_GO_term)))in g_domain):
            g_domain.add((rdflib.term.URIRef(url_prot), rdflib.term.URIRef('http://www.geneontology.org/hasAnnotation') , rdflib.term.URIRef(url_GO_term)))
        else:
            g_domain.add((rdflib.term.URIRef(url_prot), RDF.type, rdflib.BNode()))

    file_annot.close()
    return g_domain



def buildGraph_HPO(ontology_file_path, annotations_file_path):
    """
    Builds the KG for HPO (HPO + HPO annotations).
    :param ontology_file_path: HPO ontology file path in owl format;
    :param annotations_file_path: HPO annotations file path in tsv format;
    :return: a HPO KG.
    """
    g = rdflib.Graph()
    g.parse(ontology_file_path, format='xml')
    
    file_annot = open(annotations_file_path, 'r')
    for annot in file_annot:
        gene, hp_term = annot[:-1].split('\t')
        url_gene = "http://purl.obolibrary.org/obo/" + gene
        url_hp_term = 'http://purl.obolibrary.org/obo/HP_' + hp_term
        g.add((rdflib.term.URIRef(url_gene),
                   rdflib.term.URIRef('http://purl.obolibrary.org/obo/hasAnnotation'),
                   rdflib.term.URIRef(url_hp_term)))
    file_annot.close()
    return g



def build_KG_domain_HPO(ontology_file_path, annotations_file_path, domain, prots):
    """
    Builds the KG for a GO semantic aspect.
    :param ontology_file_path: GO ontology file path in owl format;
    :param annotations_file_path: GOA annotations file path in GAF 2.1 version;
    :param domain: semantic aspect. Domain can be "molecular_function", "biological_process", "cellular_component";
    :param prots: list of prots for which embeddings will be computed;
    :return: a KG for a GO semantic aspect.
    """
    g = rdflib.Graph()
    g_domain = rdflib.Graph()
    # Process ontology file
    g.parse(ontology_file_path, format='xml')

    for (sub, pred, obj) in g.triples((None,None, None)):
        if g.__contains__((sub, rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'), rdflib.term.Literal(domain, datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')))):
            g_domain.add(((sub, pred, obj)))

    file_annot = open(annotations_file_path , 'r')
    file_annot.readline()
    for annot in file_annot:
        list_annot = annot.split('\t')
        id_prot, GO_term = list_annot[1], list_annot[4]
        url_GO_term = "http://purl.obolibrary.org/obo/GO_" + GO_term.split(':')[1]
        url_prot = "http://" + id_prot
        if ((rdflib.term.URIRef(url_GO_term), None, None) in g_domain) or ((None, None, (rdflib.term.URIRef(url_GO_term)))in g_domain):
            g_domain.add((rdflib.term.URIRef(url_prot), rdflib.term.URIRef('http://www.geneontology.org/hasAnnotation') , rdflib.term.URIRef(url_GO_term)))
        else:
            g_domain.add((rdflib.term.URIRef(url_prot), RDF.type, rdflib.BNode()))
    file_annot.close()

    for url_prot in prots:
        g_domain.add((rdflib.term.URIRef(url_prot), RDF.type, rdflib.BNode()))
    
    return g_domain



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
    


