import os
import sys
import argparse
import sys
import tempfile

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


########################################################################################################################
##############################################         Construct KGs        ############################################
########################################################################################################################


def generate_annotations_tsv(annotations_file_path, new_annotations_file_path):

    file_annot = open(annotations_file_path , 'r')
    new_file_annot = open(new_annotations_file_path, 'w')
    file_annot.readline()

    # prots = {}
    for annot in file_annot:
        list_annot = annot.split('\t')
        id_prot, GO_term = list_annot[1], list_annot[4]
        url_GO_term = "http://purl.obolibrary.org/obo/GO_" + GO_term.split(':')[1]
        url_prot = "http://www.uniprot.org/uniprot/" + id_prot
        new_file_annot.write(url_prot + ' <' + url_GO_term + '>' + '\n')

        # if url_prot in prots:
        #     prots[url_prot] = prots[url_prot] + [url_GO_term]
        # else:
        #     prots[url_prot] = [url_GO_term]
    # for prot in prots:
    #     annots = prots[prot]
    #     new_file_annot.write(prot + '	' + annots[0])
    #     for annot in annots[1:]:
    #         new_file_annot.write(';' + annot)
    #         new_file_annot.write('\n')

    new_file_annot.close()
    file_annot.close()

########################################################################################################################
##############################################        Call Embeddings       ############################################
########################################################################################################################

def run_embedddings_prots_aspect(path_opa2vec, ontology_file, annotations_file_path, vector_size, type_word2vec, path_output, path_entity_file, GO_domains, dataset, model_word2vec, pretrained, window=5, mincount=0, listofuri="all", reasoner="elk", annot="no"):

    for domain in GO_domains:

        annotations_file_path_domain = annotations_file_path + '_' + domain + '.gaf'
        new_annotations_file_path_domain = annotations_file_path + '_' + domain + '.tsv'
        outfile = path_output + domain + '/Embeddings_' + dataset + '_opa2vec_skip-gram_' + domain + '.txt'
        ensure_dir(path_output + domain + '/')
        generate_annotations_tsv(annotations_file_path_domain, new_annotations_file_path_domain)

        # Create the needed temporary files
        # 1. For ontology processing
        axiomsinf = tempfile.NamedTemporaryFile()
        axiomsorig = tempfile.NamedTemporaryFile()
        classesfile = tempfile.NamedTemporaryFile()
        axioms = tempfile.NamedTemporaryFile()
        # 2. For metadata extraction
        metadatafile = tempfile.NamedTemporaryFile()
        annotated_meta = tempfile.NamedTemporaryFile()
        # 3. For class extraction
        annot_classes = tempfile.NamedTemporaryFile()
        allclasses = tempfile.NamedTemporaryFile()
        finalclasses = tempfile.NamedTemporaryFile()
        # 4. For associations
        AssoAxiomInferred = tempfile.NamedTemporaryFile()
        Assoc1 = tempfile.NamedTemporaryFile()
        Assoc2 = tempfile.NamedTemporaryFile()
        # 5. For vector production
        ontology_corpus = tempfile.NamedTemporaryFile()
        tempvecs = tempfile.NamedTemporaryFile()

        ###################################################################################################################
        print("	\n		*********** OPA2Vec Running ... ***********\n")

        # 1. Extract ontology axioms and classes
        print("\n		1.Ontology Processing ...\n")
        cmdonto = "groovy " + path_opa2vec + "ProcessOntology.groovy " + str(ontology_file) + " " + str(reasoner) + " " + str(
            axiomsinf.name) + " " + str(axiomsorig.name) + " " + str(classesfile.name)
        os.system(cmdonto)
        cmdMerge = "cat " + str(axiomsorig.name) + " " + str(axiomsinf.name) + " >" + str(axioms.name)
        os.system(cmdMerge)
        cmdgetclas = "perl " + path_opa2vec + "getclasses.pl " + str(new_annotations_file_path_domain) + " " + str(annot_classes.name)
        os.system(cmdgetclas)
        cmdclas1 = "cat " + str(classesfile.name) + " " + str(annot_classes.name) + " > " + str(allclasses.name)
        os.system(cmdclas1)
        cmdclas2 = "sort -u " + str(allclasses.name) + " > " + str(finalclasses.name)
        os.system(cmdclas2)
        print("\n   ######################################################################\n")

        # 2. Extract and annotate metadata
        print("\n		2.Metadata Extraction ...\n")
        cmdmeta = "groovy " + path_opa2vec + "getMetadata.groovy " + str(ontology_file) + " " + str(listofuri) + " " + str(metadatafile.name)
        os.system(cmdmeta)
        if (annot == 'yes' or annot == 'Yes' or annot == 'YES'):
            print("\n 	2.1. Metadata annotation ...")
            cmdannotat = "perl " + path_opa2vec + "AnnotateMetadata.pl" + str(metadatafile.name) + "> " + str(annotated_meta.name)
            os.system(cmdannotat)
        print("\n   ######################################################################\n")

        # 3. Process associations
        print("\n		3.Propagate Associations through hierarchy ...\n")
        cmdanc = "perl " + path_opa2vec + "AddAncestors.pl " + str(new_annotations_file_path_domain) + " " + str(axioms.name) + " " + str(
            classesfile.name) + " " + str(AssoAxiomInferred.name)
        os.system(cmdanc)
        cmdasso = "cat " + str(new_annotations_file_path_domain) + " " + str(AssoAxiomInferred.name) + " > " + str(Assoc1.name)
        os.system(cmdasso)
        cmdsort = "sort -u " + str(Assoc1.name) + " > " + str(Assoc2.name)
        os.system(cmdsort)
        print("\n   ######################################################################\n")

        # 4. Create corpus
        print("\n		4.Corpus Creation ...\n")
        if (annot == 'yes' or annot == 'Yes' or annot == 'YES'):
            cmdcorpus = "cat " + str(axioms.name) + " " + str(annotated_meta.name) + " " + str(Assoc2.name) + " > " + str(
                ontology_corpus.name)
        else:
            cmdcorpus = "cat " + path_opa2vec + "axioms.lst " + path_opa2vec + "metadata.lst " + path_opa2vec + "AllAssociations.lst  > " + path_opa2vec + "ontology_corpus.lst"
            cmdcorpus = "cat " + str(axioms.name) + " " + str(metadatafile.name) + " " + str(Assoc2.name) + " > " + str(
                ontology_corpus.name)

        os.system(cmdcorpus)
        print("\n  ######################################################################\n")

        # 5. Run Word2Vec
        tempoutfile = "tempout"
        print("\n		5.Running Word2Vec ... \n")
        cmdwv = "python3 " + path_opa2vec + "runWord2Vec.py " + str(finalclasses.name) + " " + str(window) + " " + str(vector_size) + " " + str(mincount) + " " + str(model_word2vec) + " " + str(pretrained) + " " + str(ontology_corpus.name) + ' "' + str(outfile) + '" "' +  path_entity_file +  '" '
        os.system(cmdwv)
        print("		*********** Vector representations created ***********\n")

        # 6. Finalize and clean-up
        print("\n		*********** OPA2Vec Complete ***********\n")

        axiomsinf.close()
        axiomsorig.close()
        classesfile.close()
        axioms.close()
        metadatafile.close()
        annotated_meta.close()
        annot_classes.close()
        finalclasses.close()
        AssoAxiomInferred.close()
        Assoc1.close()
        Assoc2.close()
        ontology_corpus.close()



if __name__== '__main__':

    #################################### Parameters ####################################
    vector_size = 200
    model_word2vec = "sg"
    pretrained = "SS_EmbeddingsWithBiasedWalks_Calculation/pyrdf2vec2/RepresentationModel_pubmed.txt"
    path_opa2vec = "SS_EmbeddingsWithBiasedWalks_Calculation/opa2vec/"

    # #################################### STRINGv11 Datasets ####################################
    # dataset = "STRING_v11"
    # ontology_file = "Data/Original_STRINGdatasets/v11/go-basic.owl"
    # path_output = 'SS_EmbeddingsWithBiasedWalks_Calculation/Embeddings/' + dataset + '/'
    # ensure_dir(path_output)
    # annotations_file_path = "Data/Original_STRINGdatasets/v11/AnnotationsPerAspect/goa_human_new"
    # path_entity_file = "Data/Processed_STRINGdatasets/v11/Prots_v11(score950).txt"
    #
    # GO_domains = ["biological_process", "cellular_component", "molecular_function", "molecular_function_regulator", "antioxidant_activity",
    #                 "nutrient_reservoir_activity", "molecular_transducer_activity",
    #                 "small_molecule_sensor_activity", "molecular_template_activity",
    #                 "toxin_activity", "binding",
    #                 "cargo_receptor_activity", "translation_regulator_activity",
    #                 "protein_folding_chaperone", "catalytic_activity",
    #                 "protein_tag", "structural_molecule_activity",
    #                 "molecular_carrier_activity", "fusogenic_activity",
    #                 "molecular_sequestering_activity","molecular_adaptor_activity",
    #                 "transporter_activity", "other_organism_part",
    #                 "virion_part", "virion",
    #                 "protein-containing_complex", "cellular_anatomical_entity",
    #                 "biological_adhesion","localization",
    #                 "multicellular_organismal_process", "metabolic_process",
    #                 "cellular_process", "developmental_process",
    #                 "phosphorus_utilization", "signaling",
    #                 "sulfur_utilization","locomotion",
    #                 "behavior", "pigmentation",
    #                 "carbon_utilization", "biological_regulation",
    #                 "biological_phase", "immune_system_process",
    #                 "growth", "carbohydrate_utilization",
    #                 "reproductive_process", "rhythmic_process",
    #                 "reproduction", "interspecies_interaction_between_organisms",
    #                 "biomineralization", "detoxification",
    #                 "multi-organism_process", "nitrogen_utilization",
    #                 "intraspecies_interaction_between_organisms", "response_to_stimulus"]
    #
    # run_embedddings_prots_aspect(path_opa2vec, ontology_file, annotations_file_path, vector_size, model_word2vec,
    #                              path_output, path_entity_file, GO_domains, dataset, model_word2vec, pretrained)
    #
    #
    #
    # ################################## kgsim Datasets (v2) ####################################
    #
    # dataset = "ALL"
    # path_output = 'SS_EmbeddingsWithBiasedWalks_Calculation/Embeddings/kgsim2(GO2021)/'
    # ensure_dir(path_output)
    # ontology_file = "Data/Original_STRINGdatasets/v11/go-basic.owl"
    # path_entity_file = "Data/Processed_kgsimDatasets2/Prots_4species(ALL).txt"
    # annotations_file_path = 'Data/Processed_kgsimDatasets/AnnotationsPerAspect/goa_4species_new'
    #
    # GO_domains = ["biological_process", "cellular_component", "molecular_function", "molecular_function_regulator", "antioxidant_activity",
    #                    "nutrient_reservoir_activity", "molecular_transducer_activity",
    #                    "small_molecule_sensor_activity", "molecular_template_activity",
    #                    "toxin_activity", "binding",
    #                    "cargo_receptor_activity", "translation_regulator_activity",
    #                    "protein_folding_chaperone", "catalytic_activity",
    #                    "protein_tag", "structural_molecule_activity",
    #                    "molecular_carrier_activity", "fusogenic_activity",
    #                    "molecular_sequestering_activity","molecular_adaptor_activity",
    #                    "transporter_activity", "other_organism_part",
    #                    "virion_part", "virion",
    #                    "protein-containing_complex", "cellular_anatomical_entity",
    #                    "biological_adhesion","localization",
    #                    "multicellular_organismal_process", "metabolic_process",
    #                    "cellular_process", "developmental_process",
    #                    "phosphorus_utilization", "signaling",
    #                    "sulfur_utilization","locomotion",
    #                    "behavior", "pigmentation",
    #                    "carbon_utilization", "biological_regulation",
    #                    "biological_phase", "immune_system_process",
    #                    "growth", "carbohydrate_utilization",
    #                    "reproductive_process", "rhythmic_process",
    #                    "reproduction", "interspecies_interaction_between_organisms",
    #                    "biomineralization", "detoxification",
    #                    "multi-organism_process", "nitrogen_utilization",
    #                    "intraspecies_interaction_between_organisms", "response_to_stimulus",
    #                    "molecular_function", "cellular_component" , "biological_process"]
    #
    # run_embedddings_prots_aspect(path_opa2vec, ontology_file, annotations_file_path, vector_size,
    #                              model_word2vec,path_output, path_entity_file, GO_domains, dataset, model_word2vec, pretrained)
    #
    #
