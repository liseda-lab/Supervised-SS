package SS_Calculation;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Set;
import java.util.Collections;

import org.openrdf.model.URI;
import slib.graph.algo.extraction.rvf.instances.InstancesAccessor;
import slib.graph.algo.extraction.rvf.instances.impl.InstanceAccessor_RDF_TYPE;
import slib.graph.algo.utils.GAction;
import slib.graph.algo.utils.GActionType;
import slib.graph.algo.utils.GraphActionExecutor;
import slib.graph.io.conf.GDataConf;
import slib.graph.io.loader.GraphLoaderGeneric;
import slib.graph.io.loader.annot.GraphLoader_TSVannot;
import slib.graph.io.util.GFormat;
import slib.graph.model.graph.G;
import slib.graph.model.impl.graph.memory.GraphMemory;
import slib.graph.model.impl.repo.URIFactoryMemory;
import slib.graph.model.repo.URIFactory;
import slib.sml.sm.core.engine.SM_Engine;
import slib.sml.sm.core.metrics.ic.utils.IC_Conf_Corpus;
import slib.sml.sm.core.metrics.ic.utils.IC_Conf_Topo;
import slib.sml.sm.core.metrics.ic.utils.ICconf;
import slib.sml.sm.core.utils.SMConstants;
import slib.sml.sm.core.utils.SMconf;
import slib.utils.ex.SLIB_Ex_Critic;
import slib.utils.ex.SLIB_Exception;
import slib.utils.impl.Timer;
import java.util.HashMap;

/*
This class is responsible for convertng GAF 2.1 to GAF 2.0, the format accepted by SML
 */
class Convert_GAF_versions {
    // 2 arguments: annot and new_annot
    // annot is the file annotations path in GAF.2.1 version
    // new_annot is the new file annotations path in GAF 2.0 version
    public String annot;
    public String new_annot;

    public Convert_GAF_versions(String arg1, String arg2){
        annot = arg1;
        new_annot = arg2;
    }

    public void run() throws FileNotFoundException , IOException {

        PrintWriter new_file = new PrintWriter(new_annot);
        new_file.println("!gaf-version: 2.0");

        // Open the file with annotations
        FileInputStream file_annot = new FileInputStream(annot);
        BufferedReader br = new BufferedReader(new InputStreamReader(file_annot));

        String strLine;
        // Read file line by line
        while ((strLine = br.readLine()) != null){

            if (!strLine.startsWith("!") || !strLine.isEmpty() || strLine != null  || strLine!= ""){

                ArrayList<String> fields = new ArrayList<String>(Arrays.asList(strLine.split("\t")));

                if (fields.size()>12){ // verify if the annotation have taxon
                    fields.set(7 , fields.get(7).replace("," , "|"));
                    String newLine = String.join("\t" , fields);
                    new_file.println(newLine);
                }
            }
        }
        new_file.close();
        file_annot.close();
    }
}



/*
This class is responsible for calculating SSM for a list of gene pairs (using GO and HPO)
 */
class Calculate_sim_gene {
    // 8 arguments: path_file_HPO, path_file_GO, annot_HPO, annot_GO, SSM_files, dataset_files_HPO, dataset_files_GO, and SSM.
    // path_file_HPO is the HPO ontology file path
    // path_file_GO is the GO ontology file path
    // annot_HPO is the HPO annotations file path in tsv format
    // annot_GO is the GO annotations file path in GAF 2.0 version
    // SSM_files is the list of semantic similarity files paths for each element of the dasets_files
    // dataset_files_HPO is the list of dataset files path with the pairs of genes. The format of each line of the dataset files is "Gene1  Gene2   Proxy"
    // dataset_files_GO is the list of dataset files path with the pairs of proteins. The format of each line of the dataset files is "Prot1  Prot2   Proxy"
    // SSM is the semantic similarity measure. If all, the 6 standard measures are chosen.
    public String path_file_HPO;
    public String path_file_GO;
    public String annot_HPO;
    public String annot_GO;
    public String[] SSM_files;
    public String[] dataset_files_HPO;
    public String[] dataset_files_GO;
    public String SSM;

    public Calculate_sim_gene(String arg1, String arg2, String[] arg3, String[] arg4, String arg5, String arg6, String arg7, String[] arg8) {
        path_file_HPO = arg1;
        annot_HPO = arg2;
        SSM_files = arg3;
        dataset_files_HPO = arg4;
        SSM = arg5;
        path_file_GO = arg6;
        annot_GO = arg7;
        dataset_files_GO = arg8;
    }

    public void run() throws SLIB_Exception, FileNotFoundException, IOException {

        Timer t = new Timer();
        t.start();

        URIFactory factory_hpo = URIFactoryMemory.getSingleton();
        URI graph_uri_hpo = factory_hpo.getURI("http://purl.obolibrary.org/obo/HP_");
        URI graph_uri_hpo2 = factory_hpo.getURI("http://purl.obolibrary.org/obo/");
        factory_hpo.loadNamespacePrefix("HP", graph_uri_hpo.toString());

        G graph_hpo = new GraphMemory(graph_uri_hpo2);
        GDataConf hpoConf = new GDataConf(GFormat.RDF_XML, path_file_HPO);

        GDataConf hpo_annotConf = new GDataConf(GFormat.TSV_ANNOT, annot_HPO);
        hpo_annotConf.addParameter(GraphLoader_TSVannot.PARAM_PREFIX_SUBJECT, "http://purl.obolibrary.org/obo/");
        hpo_annotConf.addParameter(GraphLoader_TSVannot.PARAM_PREFIX_OBJECT, "http://purl.obolibrary.org/obo/HP_");
        hpo_annotConf.addParameter(GraphLoader_TSVannot.PARAM_HEADER, "false");

        GraphLoaderGeneric.populate(hpoConf, graph_hpo);
        GraphLoaderGeneric.populate(hpo_annotConf, graph_hpo);

        URI URL_hpo = factory_hpo.getURI("http://purl.obolibrary.org/obo/HP_0000001");
        GAction reduction_hpo = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_hpo.addParameter("root_uri", URL_hpo.stringValue());
        GraphActionExecutor.applyAction(factory_hpo, reduction_hpo, graph_hpo);


        URIFactory factory_go = URIFactoryMemory.getSingleton();
        URI graph_uri_go = factory_go.getURI("http://purl.obolibrary.org/obo/GO_");
        URI graph_uri = factory_go.getURI("http://");

        factory_go.loadNamespacePrefix("GO", graph_uri_go.toString());

        G graph_BP = new GraphMemory(graph_uri);
        G graph_CC = new GraphMemory(graph_uri);
        G graph_MF = new GraphMemory(graph_uri);

        GDataConf goConf = new GDataConf(GFormat.RDF_XML, path_file_GO);
        GDataConf go_annotConf = new GDataConf(GFormat.GAF2, annot_GO);

        GraphLoaderGeneric.populate(goConf, graph_BP);
        GraphLoaderGeneric.populate(goConf, graph_CC);
        GraphLoaderGeneric.populate(goConf, graph_MF);

        GraphLoaderGeneric.populate(go_annotConf, graph_BP);
        GraphLoaderGeneric.populate(go_annotConf, graph_CC);
        GraphLoaderGeneric.populate(go_annotConf, graph_MF);

        URI bpGOTerm = factory_go.getURI("http://purl.obolibrary.org/obo/GO_0008150");
        GAction reduction_bp = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_bp.addParameter("root_uri", bpGOTerm.stringValue());
        GraphActionExecutor.applyAction(factory_go, reduction_bp, graph_BP);

        URI ccGOTerm = factory_go.getURI("http://purl.obolibrary.org/obo/GO_0005575");
        GAction reduction_cc = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_cc.addParameter("root_uri", ccGOTerm.stringValue());
        GraphActionExecutor.applyAction(factory_go, reduction_cc, graph_CC);

        URI mfGOTerm = factory_go.getURI("http://purl.obolibrary.org/obo/GO_0003674");
        GAction reduction_mf = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_mf.addParameter("root_uri", mfGOTerm.stringValue());
        GraphActionExecutor.applyAction(factory_go, reduction_mf, graph_MF);

        if (SSM.equals("all")) {
            int i = 0;
            for (String dataset_filename : dataset_files_HPO) {
                ArrayList<String> pair_genes = get_genes_dataset(dataset_filename);
                ArrayList<String> pair_prots = get_proteins_dataset(dataset_files_GO[i]);
                semantic_measures_2genes(graph_hpo, graph_BP, graph_CC, graph_MF, factory_hpo, factory_go, pair_genes, pair_prots, SSM_files[i]);
                i++;
            }
        } else {
            int i = 0;
            for (String dataset_filename : dataset_files_HPO) {
                ArrayList<String> pair_genes = get_genes_dataset(dataset_filename);
                ArrayList<String> pair_prots = get_proteins_dataset(dataset_files_GO[i]);
                given_semantic_measures_2prots(graph_hpo, graph_BP, graph_CC, graph_MF, factory_hpo, factory_go, pair_genes, pair_prots, SSM_files[i], SSM);
                i++;
            }
        }
        t.stop();
        t.elapsedTime();
    }

    private ArrayList<String> get_genes_dataset(String dataset_filename) throws IOException {

        FileInputStream file_dataset = new FileInputStream(dataset_filename);
        BufferedReader br = new BufferedReader(new InputStreamReader(file_dataset));

        ArrayList<String> pairs_genes = new ArrayList<>();
        String strLine;
        //String head = br.readLine();
        // Read file line by line
        while ((strLine = br.readLine()) != null) {
            strLine = strLine.substring(0, strLine.length() - 1);
            pairs_genes.add(strLine);
        }
        file_dataset.close();
        return pairs_genes;
    }

    private ArrayList<String> get_proteins_dataset(String dataset_filename) throws IOException {

        FileInputStream file_dataset = new FileInputStream(dataset_filename);
        BufferedReader br = new BufferedReader(new InputStreamReader(file_dataset));

        ArrayList<String> pairs_prots = new ArrayList<>();
        String strLine;
        // Read file line by line
        while ((strLine = br.readLine()) != null) {
            strLine = strLine.substring(0, strLine.length() - 1);
            pairs_prots.add(strLine);
        }
        file_dataset.close();
        return pairs_prots;
    }

    private void groupwise_measure_file(G graph_hpo, G graph_BP, G graph_CC, G graph_MF, SM_Engine engine_hpo, SM_Engine engine_BP, SM_Engine engine_CC, SM_Engine engine_MF, URIFactory factory_hpo, URIFactory factory_go, ArrayList<String> pairs_prots, ArrayList<String> pairs_genes, String SSM_file, SMconf ssm) throws SLIB_Ex_Critic, FileNotFoundException {

        double sim_hpo, sim_BP, sim_CC, sim_MF;
        PrintWriter file = new PrintWriter(SSM_file);

        int idx = 0;
        for (String pair_prot : pairs_prots) {

            String pair_gene = pairs_genes.get(idx);
            ArrayList<String> genes = new ArrayList<String>(Arrays.asList(pair_gene.split("\t")));
            String uri_gene1 = "http://purl.obolibrary.org/obo/" + genes.get(0);
            String uri_gene2 = "http://purl.obolibrary.org/obo/" + genes.get(1);
            String gene1_id = genes.get(0);
            String gene2_id = genes.get(1);
            URI gene_instance1 = factory_hpo.getURI(uri_gene1);
            URI gene_instance2 = factory_hpo.getURI(uri_gene2);

            InstancesAccessor gene_instance1_acessor_hpo = new InstanceAccessor_RDF_TYPE(graph_hpo);
            Set<URI> annotations_instance1_hpo = gene_instance1_acessor_hpo.getDirectClass(gene_instance1);
            InstancesAccessor gene_instance2_acessor_hpo = new InstanceAccessor_RDF_TYPE(graph_hpo);
            Set<URI> annotations_instance2_hpo = gene_instance2_acessor_hpo.getDirectClass(gene_instance2);

            ArrayList<String> proteins = new ArrayList<String>(Arrays.asList(pair_prot.split("\t")));
            String uri_prot1 = "http://" + proteins.get(0);
            String uri_prot2 = "http://" + proteins.get(1);
            URI prot_instance1 = factory_go.getURI(uri_prot1);
            URI prot_instance2 = factory_go.getURI(uri_prot2);

            InstancesAccessor gene_instance1_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
            Set<URI> annotations_instance1_BP = gene_instance1_acessor_bp.getDirectClass(prot_instance1);
            InstancesAccessor gene_instance1_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
            Set<URI> annotations_instance1_CC = gene_instance1_acessor_cc.getDirectClass(prot_instance1);
            InstancesAccessor gene_instance1_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
            Set<URI> annotations_instance1_MF = gene_instance1_acessor_mf.getDirectClass(prot_instance1);

            InstancesAccessor gene_instance2_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
            Set<URI> annotations_instance2_BP = gene_instance2_acessor_bp.getDirectClass(prot_instance2);
            InstancesAccessor gene_instance2_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
            Set<URI> annotations_instance2_CC = gene_instance2_acessor_cc.getDirectClass(prot_instance2);
            InstancesAccessor gene_instance2_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
            Set<URI> annotations_instance2_MF = gene_instance2_acessor_mf.getDirectClass(prot_instance2);

            if (annotations_instance1_hpo.isEmpty() || annotations_instance2_hpo.isEmpty()) {
                sim_hpo = 0;
            } else {
                sim_hpo = engine_hpo.compare(ssm, annotations_instance1_hpo, annotations_instance2_hpo);
            }
            if (annotations_instance1_BP.isEmpty() || annotations_instance2_BP.isEmpty()) {
                sim_BP = 0;
            } else {
                sim_BP = engine_BP.compare(ssm, annotations_instance1_BP, annotations_instance2_BP);
            }
            if (annotations_instance1_CC.isEmpty() || annotations_instance2_CC.isEmpty()) {
                sim_CC = 0;
            } else {
                sim_CC = engine_CC.compare(ssm, annotations_instance1_CC, annotations_instance2_CC);
            }
            if (annotations_instance1_MF.isEmpty() || annotations_instance2_MF.isEmpty()) {
                sim_MF = 0;
            } else {
                sim_MF = engine_MF.compare(ssm, annotations_instance1_MF, annotations_instance2_MF);
            }
            file.print(uri_gene1 + "\t" + uri_gene2 + "\t" + sim_hpo + "\t" + sim_BP + "\t" + sim_CC + "\t" + sim_MF + "\n");
            file.flush();
            idx = idx + 1;
        }
        file.close();
    }

    private void pairwise_measure_file(G graph_hpo, G graph_BP, G graph_CC, G graph_MF, SM_Engine engine_hpo, SM_Engine engine_BP, SM_Engine engine_CC, SM_Engine engine_MF, URIFactory factory_hpo, URIFactory factory_go, ArrayList<String> pairs_prots, ArrayList<String> pairs_genes, String SSM_file, SMconf ssm, SMconf aggregation) throws SLIB_Ex_Critic, FileNotFoundException {

        double sim_hpo, sim_BP, sim_CC, sim_MF;
        PrintWriter file = new PrintWriter(SSM_file);

        int idx = 0;
        for (String pair_prot : pairs_prots) {

            String pair_gene = pairs_genes.get(idx);
            ArrayList<String> genes = new ArrayList<String>(Arrays.asList(pair_gene.split("\t")));
            String uri_gene1 = "http://purl.obolibrary.org/obo/" + genes.get(0);
            String uri_gene2 = "http://purl.obolibrary.org/obo/" + genes.get(1);
            String gene1_id = genes.get(0);
            String gene2_id = genes.get(1);
            URI gene_instance1 = factory_hpo.getURI(uri_gene1);
            URI gene_instance2 = factory_hpo.getURI(uri_gene2);

            InstancesAccessor gene_instance1_acessor_hpo = new InstanceAccessor_RDF_TYPE(graph_hpo);
            Set<URI> annotations_instance1_hpo = gene_instance1_acessor_hpo.getDirectClass(gene_instance1);
            InstancesAccessor gene_instance2_acessor_hpo = new InstanceAccessor_RDF_TYPE(graph_hpo);
            Set<URI> annotations_instance2_hpo = gene_instance2_acessor_hpo.getDirectClass(gene_instance2);

            ArrayList<String> proteins = new ArrayList<String>(Arrays.asList(pair_prot.split("\t")));
            String uri_prot1 = "http://" + proteins.get(0);
            String uri_prot2 = "http://" + proteins.get(1);
            URI prot_instance1 = factory_go.getURI(uri_prot1);
            URI prot_instance2 = factory_go.getURI(uri_prot2);

            InstancesAccessor gene_instance1_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
            Set<URI> annotations_instance1_BP = gene_instance1_acessor_bp.getDirectClass(prot_instance1);
            InstancesAccessor gene_instance1_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
            Set<URI> annotations_instance1_CC = gene_instance1_acessor_cc.getDirectClass(prot_instance1);
            InstancesAccessor gene_instance1_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
            Set<URI> annotations_instance1_MF = gene_instance1_acessor_mf.getDirectClass(prot_instance1);

            InstancesAccessor gene_instance2_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
            Set<URI> annotations_instance2_BP = gene_instance2_acessor_bp.getDirectClass(prot_instance2);
            InstancesAccessor gene_instance2_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
            Set<URI> annotations_instance2_CC = gene_instance2_acessor_cc.getDirectClass(prot_instance2);
            InstancesAccessor gene_instance2_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
            Set<URI> annotations_instance2_MF = gene_instance2_acessor_mf.getDirectClass(prot_instance2);

            if (annotations_instance1_hpo.isEmpty() || annotations_instance2_hpo.isEmpty()) {
                sim_hpo = 0;
            } else {
                sim_hpo = engine_hpo.compare(aggregation, ssm, annotations_instance1_hpo, annotations_instance2_hpo);
            }

            if (annotations_instance1_BP.isEmpty() || annotations_instance2_BP.isEmpty()) {
                sim_BP = 0;
            } else {
                sim_BP = engine_BP.compare(aggregation, ssm, annotations_instance1_BP, annotations_instance2_BP);
            }

            if (annotations_instance1_CC.isEmpty() || annotations_instance2_CC.isEmpty()) {
                sim_CC = 0;
            } else {
                sim_CC = engine_CC.compare(aggregation, ssm, annotations_instance1_CC, annotations_instance2_CC);
            }

            if (annotations_instance1_MF.isEmpty() || annotations_instance2_MF.isEmpty()) {
                sim_MF = 0;
            } else {
                sim_MF = engine_MF.compare(aggregation, ssm, annotations_instance1_MF, annotations_instance2_MF);
            }

            file.print(uri_gene1 + "\t" + uri_gene2
                    + "\t" + sim_hpo + "\t" + sim_BP + "\t" + sim_CC + "\t" + sim_MF + "\n");
            file.flush();

            idx = idx + 1;
        }
        file.close();

    }


    private void semantic_measures_2genes(G graph_hpo, G graph_BP, G graph_CC, G graph_MF, URIFactory factory_hpo, URIFactory factory_go, ArrayList<String> pairs_genes, ArrayList<String> pairs_prots, String
            SSM_file) throws SLIB_Ex_Critic, FileNotFoundException {

        ICconf ic_Seco = new IC_Conf_Topo("Seco", SMConstants.FLAG_ICI_SECO_2004);
        ICconf ic_Resnik = new IC_Conf_Corpus("resnik", SMConstants.FLAG_IC_ANNOT_RESNIK_1995_NORMALIZED);

        SMconf SimGIC_icSeco = new SMconf("gic", SMConstants.FLAG_SIM_GROUPWISE_DAG_GIC);
        SimGIC_icSeco.setICconf(ic_Seco);

        SMconf SimGIC_icResnik = new SMconf("gic", SMConstants.FLAG_SIM_GROUPWISE_DAG_GIC);
        SimGIC_icResnik.setICconf(ic_Resnik);

        SMconf Resnik_icSeco = new SMconf("resnik", SMConstants.FLAG_SIM_PAIRWISE_DAG_NODE_RESNIK_1995);
        Resnik_icSeco.setICconf(ic_Seco);

        SMconf Resnik_icResnik = new SMconf("resnik", SMConstants.FLAG_SIM_PAIRWISE_DAG_NODE_RESNIK_1995);
        Resnik_icResnik.setICconf(ic_Resnik);

        SMconf max = new SMconf("max", SMConstants.FLAG_SIM_GROUPWISE_MAX);
        SMconf bma = new SMconf("bma", SMConstants.FLAG_SIM_GROUPWISE_BMA);

        SM_Engine engine_hpo = new SM_Engine(graph_hpo);
        SM_Engine engine_bp = new SM_Engine(graph_BP);
        SM_Engine engine_cc = new SM_Engine(graph_CC);
        SM_Engine engine_mf = new SM_Engine(graph_MF);

        ArrayList<String> pre_filename = new ArrayList<String>(Arrays.asList(SSM_file.split("/ss_")));
        File theDir = new File(pre_filename.get(0));
        if (!theDir.exists()) {
            theDir.mkdirs();
        }

        String filename_SimGIC_icSeco = pre_filename.get(0) + "/ss_simGIC_ICSeco" + "_" + pre_filename.get(1);
        groupwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_SimGIC_icSeco, SimGIC_icSeco);
        String filename_SimGIC_icResnik = pre_filename.get(0) + "/ss_simGIC_ICResnik" + "_" + pre_filename.get(1);
        groupwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_SimGIC_icResnik, SimGIC_icResnik);

        String filename_ResnikMax_icSeco = pre_filename.get(0) + "/ss_ResnikMax_ICSeco" + "_" + pre_filename.get(1);
        pairwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_ResnikMax_icSeco, Resnik_icSeco, max);
        String filename_ResnikMax_icResnik = pre_filename.get(0) + "/ss_ResnikMax_ICResnik" + "_" + pre_filename.get(1);
        pairwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_ResnikMax_icResnik, Resnik_icResnik, max);

        String filename_ResnikBMA_icSeco = pre_filename.get(0) + "/ss_ResnikBMA_ICSeco" + "_" + pre_filename.get(1);
        pairwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_ResnikBMA_icSeco, Resnik_icSeco, bma);
        String filename_ResnikBMA_icResnik = pre_filename.get(0) + "/ss_ResnikBMA_ICResnik" + "_" + pre_filename.get(1);
        pairwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_ResnikBMA_icResnik, Resnik_icResnik, bma);

    }

    private void given_semantic_measures_2prots(G graph_hpo, G graph_BP, G graph_CC, G graph_MF, URIFactory factory_hpo, URIFactory factory_go, ArrayList<String> pairs_genes, ArrayList<String> pairs_prots, String
            SSM_file, String SSM) throws SLIB_Ex_Critic, FileNotFoundException {

        String[] components_ssm = SSM.split("_");
        ICconf ic;
        SMconf aggregation;
        SMconf ssm;

        HashMap<String, String> flags_ssm = new HashMap<String, String>();
        flags_ssm.put("max", SMConstants.FLAG_SIM_GROUPWISE_MAX);
        flags_ssm.put("bma", SMConstants.FLAG_SIM_GROUPWISE_BMA);
        flags_ssm.put("avg", SMConstants.FLAG_SIM_GROUPWISE_AVERAGE);
        flags_ssm.put("bmm", SMConstants.FLAG_SIM_GROUPWISE_BMM);
        flags_ssm.put("min", SMConstants.FLAG_SIM_GROUPWISE_MIN);

        flags_ssm.put("gic", SMConstants.FLAG_SIM_GROUPWISE_DAG_GIC);
        flags_ssm.put("lee", SMConstants.FLAG_SIM_GROUPWISE_DAG_LEE_2004);
        flags_ssm.put("deane", SMConstants.FLAG_SIM_GROUPWISE_DAG_ALI_DEANE);

        flags_ssm.put("resnik", SMConstants.FLAG_SIM_PAIRWISE_DAG_NODE_RESNIK_1995);
        flags_ssm.put("li", SMConstants.FLAG_SIM_PAIRWISE_DAG_EDGE_LI_2003);
        flags_ssm.put("pekarstaab", SMConstants.FLAG_SIM_PAIRWISE_DAG_EDGE_PEKAR_STAAB_2002);
        flags_ssm.put("rada", SMConstants.FLAG_SIM_PAIRWISE_DAG_EDGE_RADA_1989);

        flags_ssm.put("ICseco", SMConstants.FLAG_ICI_SECO_2004);
        flags_ssm.put("ICresnik", SMConstants.FLAG_IC_ANNOT_RESNIK_1995_NORMALIZED);
        flags_ssm.put("ICharispe", SMConstants.FLAG_ICI_HARISPE_2012);
        flags_ssm.put("ICsanchez", SMConstants.FLAG_ICI_SANCHEZ_2011);
        flags_ssm.put("ICzhou", SMConstants.FLAG_ICI_ZHOU_2008);

        SM_Engine engine_hpo = new SM_Engine(graph_hpo);
        SM_Engine engine_bp = new SM_Engine(graph_BP);
        SM_Engine engine_cc = new SM_Engine(graph_CC);
        SM_Engine engine_mf = new SM_Engine(graph_MF);

        if (components_ssm.length > 2) {
            ic = new IC_Conf_Topo(flags_ssm.get(components_ssm[2]));
            if (ic.isCorpusBased()) {
                ic = new IC_Conf_Corpus(flags_ssm.get(components_ssm[2]));
            }
            ssm = new SMconf(flags_ssm.get(components_ssm[0]));
            ssm.setICconf(ic);
            aggregation = new SMconf(flags_ssm.get(components_ssm[1]));

            String filename_SSM = SSM_file + "/ss_" + SSM + ".txt";
            pairwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_SSM, ssm, aggregation);

        } else {
            ic = new IC_Conf_Topo(flags_ssm.get(components_ssm[1]));
            if (ic.isCorpusBased()) {
                ic = new IC_Conf_Corpus(flags_ssm.get(components_ssm[1]));
            }
            ssm = new SMconf(flags_ssm.get(components_ssm[0]));
            ssm.setICconf(ic);
            String filename_SSM = SSM_file + "/ss_" + SSM + ".txt";
            groupwise_measure_file(graph_hpo, graph_BP, graph_CC, graph_MF, engine_hpo, engine_bp, engine_cc, engine_mf, factory_hpo, factory_go, pairs_prots, pairs_genes, filename_SSM, ssm);
        }
    }
}



public class Run_SS_calculation_HPOandGO_yourdataset{
    // 9 arguments: args[0], args[1], args[2], args[3], args[4],  args[5], args[6], args[7], args[8]
    // args[0] - HPO file path
    // arg[1] - annotations file path for HPO
    // arg[2] - GO file path
    // arg[3] - GO annotations file path in GAF 2.0 version
    // arg[4] - new GO annotations file path in GAF 2.1 version
    // arg[5] - dataset file path with gene ids
    // arg[6] - dataset file path with prot ids
    // arg[7] - new semantic similarity file path
    // arg[8] - SSMs (if == all, so 6 SSM)

    public static void main(String[] args) throws Exception {

        Convert_GAF_versions annot = new Convert_GAF_versions(args[4], args[3]);
        annot.run();

        Calculate_sim_gene datasets;
        if (args.length == 9) {
            datasets = new Calculate_sim_gene(args[0], args[1], new String[]{args[7]}, new String[]{args[5]}, args[8], args[2], args[3], new String[]{args[6]});
        }else {
            datasets = new Calculate_sim_gene(args[0], args[1], new String[]{args[7]}, new String[]{args[5]}, "all", args[2], args[3], new String[]{args[6]});
        }
        datasets.run();
    }
}
