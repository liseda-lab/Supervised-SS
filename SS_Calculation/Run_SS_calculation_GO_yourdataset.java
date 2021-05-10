package SS_Calculation;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Set;

import org.openrdf.model.URI;
import slib.graph.algo.extraction.rvf.instances.InstancesAccessor;
import slib.graph.algo.extraction.rvf.instances.impl.InstanceAccessor_RDF_TYPE;
import slib.graph.algo.utils.GAction;
import slib.graph.algo.utils.GActionType;
import slib.graph.algo.utils.GraphActionExecutor;
import slib.graph.io.conf.GDataConf;
import slib.graph.io.loader.GraphLoaderGeneric;
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
        // Open the file with annotations
        FileInputStream file_annot = new FileInputStream(annot);
        BufferedReader br = new BufferedReader(new InputStreamReader(file_annot));

        String first_line = br.readLine();
        if (first_line != "!gaf-version: 2.0"){
            if (first_line.startsWith("!gaf-version: 2.1")){
                PrintWriter new_file = new PrintWriter(new_annot);
                new_file.println("!gaf-version: 2.0");

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
            } else {
                throw new IOException("Incompatible version of GOA File");
            }
        }
        file_annot.close();
    }
}



/*
This class is responsible for calculating SSM for a list of protein pairs files of the same species (using same GAF file)
 */
class Calculate_sim_prot {
    // 4 arguments: path_file_GO , annot , SSM_files and dataset_files.
    // path_file_GO is the ontology file path
    // annot is the annotations file path in GAF 2.0 version
    // datasets_files is the list of dataset files path with the pairs of proteins. The format of each line of the dataset files is "Prot1  Prot2   Proxy"
    // SSM_files is the list of semantic similarity files paths for each element of the dasets_files
    public String path_file_GO;
    public String annot;
    public String[] SSM_files;
    public String[] dataset_files;
    public String SSM;

    public Calculate_sim_prot(String arg1, String arg2 , String[] arg3, String[] arg4, String arg5){
        path_file_GO = arg1;
        annot = arg2;
        SSM_files = arg3;
        dataset_files = arg4;
        SSM = arg5;
    }

    public void run() throws SLIB_Exception , FileNotFoundException , IOException{

        Timer t = new Timer();
        t.start();

        URIFactory factory = URIFactoryMemory.getSingleton();
        URI graph_uri_go = factory.getURI("http://purl.obolibrary.org/obo/GO_");
        URI graph_uri = factory.getURI("http://");

        // define a prefix in order to build valid uris from ids such as GO:XXXXX
        // (the URI associated to GO:XXXXX will be http://go/XXXXX)
        factory.loadNamespacePrefix("GO" , graph_uri_go.toString());

        G graph_BP = new GraphMemory(graph_uri);
        G graph_CC = new GraphMemory(graph_uri);
        G graph_MF = new GraphMemory(graph_uri);

        GDataConf goConf =  new GDataConf(GFormat.RDF_XML , path_file_GO);
        GDataConf annotConf = new GDataConf(GFormat.GAF2, annot);

        GraphLoaderGeneric.populate(goConf , graph_BP);
        GraphLoaderGeneric.populate(goConf , graph_CC);
        GraphLoaderGeneric.populate(goConf , graph_MF);

        GraphLoaderGeneric.populate(annotConf, graph_BP);
        GraphLoaderGeneric.populate(annotConf, graph_CC);
        GraphLoaderGeneric.populate(annotConf, graph_MF);

        URI bpGOTerm = factory.getURI("http://purl.obolibrary.org/obo/GO_0008150");
        GAction reduction_bp = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_bp.addParameter("root_uri", bpGOTerm.stringValue());
        GraphActionExecutor.applyAction(factory, reduction_bp, graph_BP);

        URI ccGOTerm = factory.getURI("http://purl.obolibrary.org/obo/GO_0005575");
        GAction reduction_cc = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_cc.addParameter("root_uri", ccGOTerm.stringValue());
        GraphActionExecutor.applyAction(factory, reduction_cc, graph_CC);

        URI mfGOTerm = factory.getURI("http://purl.obolibrary.org/obo/GO_0003674");
        GAction reduction_mf = new GAction(GActionType.VERTICES_REDUCTION);
        reduction_mf.addParameter("root_uri", mfGOTerm.stringValue());
        GraphActionExecutor.applyAction(factory, reduction_mf, graph_MF);

        if(SSM.equals("all")){
            int i = 0;
            for (String dataset_filename : dataset_files) {
                ArrayList<String> pair_prots = get_proteins_dataset(dataset_filename);
                semantic_measures_2prots(graph_BP, graph_CC, graph_MF, factory, pair_prots, SSM_files[i]);
                i++;
            }
        }else{
            int i = 0;
            for (String dataset_filename : dataset_files) {
                ArrayList<String> pair_prots = get_proteins_dataset(dataset_filename);
                given_semantic_measures_2prots(graph_BP, graph_CC, graph_MF, factory, pair_prots, SSM_files[i], SSM);
                i++;
            }
        }
        t.stop();
        t.elapsedTime();
    }

    private ArrayList<String> get_proteins_dataset(String dataset_filename) throws  IOException{

        FileInputStream file_dataset = new FileInputStream(dataset_filename);
        BufferedReader br = new BufferedReader(new InputStreamReader(file_dataset));

        ArrayList<String> pairs_prots = new ArrayList<>();
        String strLine;

        // Read file line by line
        while ((strLine = br.readLine()) != null) {
            strLine = strLine.substring(0 , strLine.length()-1);
            pairs_prots.add(strLine);
        }
        file_dataset.close();
        return pairs_prots;
    }

    private void groupwise_measure_file(G graph_BP, G graph_CC, G graph_MF, SM_Engine engine_bp, SM_Engine engine_cc, SM_Engine engine_mf, URIFactory factory, ArrayList<String> pairs_prots, String SSM_file, SMconf ssm) throws SLIB_Ex_Critic, FileNotFoundException {

        double sim_BP, sim_CC, sim_MF;
        PrintWriter file = new PrintWriter(SSM_file);

        for (String pair : pairs_prots) {
            ArrayList<String> proteins = new ArrayList<String>(Arrays.asList(pair.split("\t")));
            String uri_prot1 = "http://" + proteins.get(0);
            String uri_prot2 = "http://" + proteins.get(1);

            URI instance1 = factory.getURI(uri_prot1);
            URI instance2 = factory.getURI(uri_prot2);

            if (((graph_BP.containsVertex(instance1)) || (graph_CC.containsVertex(instance1)) || ((graph_MF.containsVertex(instance1)))) &&
                    ((graph_BP.containsVertex(instance2)) || (graph_CC.containsVertex(instance2)) || (graph_MF.containsVertex(instance2)))) {
                InstancesAccessor gene_instance1_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
                Set<URI> annotations_instance1_BP = gene_instance1_acessor_bp.getDirectClass(instance1);

                InstancesAccessor gene_instance1_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
                Set<URI> annotations_instance1_CC = gene_instance1_acessor_cc.getDirectClass(instance1);

                InstancesAccessor gene_instance1_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
                Set<URI> annotations_instance1_MF = gene_instance1_acessor_mf.getDirectClass(instance1);

                InstancesAccessor gene_instance2_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
                Set<URI> annotations_instance2_BP = gene_instance2_acessor_bp.getDirectClass(instance2);

                InstancesAccessor gene_instance2_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
                Set<URI> annotations_instance2_CC = gene_instance2_acessor_cc.getDirectClass(instance2);

                InstancesAccessor gene_instance2_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
                Set<URI> annotations_instance2_MF = gene_instance2_acessor_mf.getDirectClass(instance2);

                if (instance1.equals(instance2)) {
                    sim_BP = sim_CC = sim_MF = 1;
                } else {
                    if (annotations_instance1_BP.isEmpty() || annotations_instance2_BP.isEmpty()) {
                        sim_BP = 0;
                    } else {
                        sim_BP = engine_bp.compare(ssm, annotations_instance1_BP, annotations_instance2_BP);
                    }

                    if (annotations_instance1_CC.isEmpty() || annotations_instance2_CC.isEmpty()) {
                        sim_CC = 0;
                    } else {
                        sim_CC = engine_cc.compare(ssm, annotations_instance1_CC, annotations_instance2_CC);
                    }

                    if (annotations_instance1_MF.isEmpty() || annotations_instance2_MF.isEmpty()) {
                        sim_MF = 0;
                    } else {
                        sim_MF = engine_mf.compare(ssm, annotations_instance1_MF, annotations_instance2_MF);
                    }
                }
                file.print(instance1 + "\t" + instance2 + "\t" + sim_BP + "\t" + sim_CC + "\t" + sim_MF + "\n");
            }
        }
        file.close();
    }

    private void pairwise_measure_file(G graph_BP, G graph_CC, G graph_MF, SM_Engine engine_bp, SM_Engine engine_cc, SM_Engine engine_mf, URIFactory factory, ArrayList<String> pairs_prots, String SSM_file, SMconf ssm, SMconf aggregation) throws SLIB_Ex_Critic, FileNotFoundException {

        double sim_BP, sim_CC, sim_MF;
        PrintWriter file = new PrintWriter(SSM_file);

        for (String pair : pairs_prots) {
            ArrayList<String> proteins = new ArrayList<String>(Arrays.asList(pair.split("\t")));
            String uri_prot1 = "http://" + proteins.get(0);
            String uri_prot2 = "http://" + proteins.get(1);

            URI instance1 = factory.getURI(uri_prot1);
            URI instance2 = factory.getURI(uri_prot2);

            if (((graph_BP.containsVertex(instance1)) || (graph_CC.containsVertex(instance1)) || ((graph_MF.containsVertex(instance1)))) &&
                    ((graph_BP.containsVertex(instance2)) || (graph_CC.containsVertex(instance2)) || (graph_MF.containsVertex(instance2)))) {
                InstancesAccessor gene_instance1_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
                Set<URI> annotations_instance1_BP = gene_instance1_acessor_bp.getDirectClass(instance1);

                InstancesAccessor gene_instance1_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
                Set<URI> annotations_instance1_CC = gene_instance1_acessor_cc.getDirectClass(instance1);

                InstancesAccessor gene_instance1_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
                Set<URI> annotations_instance1_MF = gene_instance1_acessor_mf.getDirectClass(instance1);

                InstancesAccessor gene_instance2_acessor_bp = new InstanceAccessor_RDF_TYPE(graph_BP);
                Set<URI> annotations_instance2_BP = gene_instance2_acessor_bp.getDirectClass(instance2);

                InstancesAccessor gene_instance2_acessor_cc = new InstanceAccessor_RDF_TYPE(graph_CC);
                Set<URI> annotations_instance2_CC = gene_instance2_acessor_cc.getDirectClass(instance2);

                InstancesAccessor gene_instance2_acessor_mf = new InstanceAccessor_RDF_TYPE(graph_MF);
                Set<URI> annotations_instance2_MF = gene_instance2_acessor_mf.getDirectClass(instance2);

                if (instance1.equals(instance2)) {
                    sim_BP = sim_CC = sim_MF = 1;
                } else {
                    if (annotations_instance1_BP.isEmpty() || annotations_instance2_BP.isEmpty()) {
                        sim_BP = 0;
                    } else {
                        sim_BP = engine_bp.compare(aggregation, ssm, annotations_instance1_BP, annotations_instance2_BP);
                    }

                    if (annotations_instance1_CC.isEmpty() || annotations_instance2_CC.isEmpty()) {
                        sim_CC = 0;
                    } else {
                        sim_CC = engine_cc.compare(aggregation, ssm, annotations_instance1_CC, annotations_instance2_CC);
                    }

                    if (annotations_instance1_MF.isEmpty() || annotations_instance2_MF.isEmpty()) {
                        sim_MF = 0;
                    } else {
                        sim_MF = engine_mf.compare(aggregation, ssm, annotations_instance1_MF, annotations_instance2_MF);
                    }
                }
                file.print(instance1 + "\t" + instance2 + "\t" + sim_BP + "\t" + sim_CC + "\t" + sim_MF + "\n");
            }
        }
        file.close();
    }

    private void semantic_measures_2prots(G graph_BP, G graph_CC, G graph_MF, URIFactory factory, ArrayList<String> pairs_prots, String SSM_file) throws SLIB_Ex_Critic, FileNotFoundException {

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

        SM_Engine engine_bp = new SM_Engine(graph_BP);
        SM_Engine engine_cc = new SM_Engine(graph_CC);
        SM_Engine engine_mf = new SM_Engine(graph_MF);

        String filename_SimGIC_icSeco = SSM_file + "/ss_simGIC_ICSeco.txt";
        groupwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_SimGIC_icSeco, SimGIC_icSeco);
        String filename_SimGIC_icResnik = SSM_file + "/ss_simGIC_ICResnik.txt";
        groupwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_SimGIC_icResnik, SimGIC_icResnik);

        String filename_ResnikMax_icSeco = SSM_file + "/ss_ResnikMax_ICSeco.txt";
        pairwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_ResnikMax_icSeco, Resnik_icSeco, max);
        String filename_ResnikMax_icResnik = SSM_file + "/ss_ResnikMax_ICResnik.txt";
        pairwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_ResnikMax_icResnik, Resnik_icResnik, max);

        String filename_ResnikBMA_icSeco = SSM_file + "/ss_ResnikBMA_ICSeco.txt";
        pairwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_ResnikBMA_icSeco, Resnik_icSeco, bma);
        String filename_ResnikBMA_icResnik = SSM_file + "/ss_ResnikBMA_ICResnik.txt";
        pairwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_ResnikBMA_icResnik, Resnik_icResnik, bma);

    }

    private void given_semantic_measures_2prots (G graph_BP, G graph_CC, G graph_MF, URIFactory factory, ArrayList<String> pairs_prots , String SSM_file, String SSM) throws SLIB_Ex_Critic , FileNotFoundException{

        String[] components_ssm = SSM.split("_");
        ICconf ic;
        SMconf aggregation;
        SMconf ssm;

        HashMap<String, String> flags_ssm = new HashMap<String, String>();
        flags_ssm.put("max", SMConstants.FLAG_SIM_GROUPWISE_MAX);
        flags_ssm.put("bma"  , SMConstants.FLAG_SIM_GROUPWISE_BMA);
        flags_ssm.put("avg"  , SMConstants.FLAG_SIM_GROUPWISE_AVERAGE);
        flags_ssm.put("bmm"  , SMConstants.FLAG_SIM_GROUPWISE_BMM);
        flags_ssm.put("min"  , SMConstants.FLAG_SIM_GROUPWISE_MIN);

        flags_ssm.put("gic" , SMConstants.FLAG_SIM_GROUPWISE_DAG_GIC);
        flags_ssm.put("lee", SMConstants.FLAG_SIM_GROUPWISE_DAG_LEE_2004);
        flags_ssm.put("deane", SMConstants.FLAG_SIM_GROUPWISE_DAG_ALI_DEANE);

        flags_ssm.put("resnik" , SMConstants.FLAG_SIM_PAIRWISE_DAG_NODE_RESNIK_1995);
        flags_ssm.put("li" , SMConstants.FLAG_SIM_PAIRWISE_DAG_EDGE_LI_2003);
        flags_ssm.put("pekarstaab" , SMConstants.FLAG_SIM_PAIRWISE_DAG_EDGE_PEKAR_STAAB_2002);
        flags_ssm.put("rada" , SMConstants.FLAG_SIM_PAIRWISE_DAG_EDGE_RADA_1989);

        flags_ssm.put("ICseco" , SMConstants.FLAG_ICI_SECO_2004);
        flags_ssm.put("ICresnik" , SMConstants.FLAG_IC_ANNOT_RESNIK_1995_NORMALIZED);
        flags_ssm.put("ICharispe", 	SMConstants.FLAG_ICI_HARISPE_2012);
        flags_ssm.put("ICsanchez", SMConstants.FLAG_ICI_SANCHEZ_2011);
        flags_ssm.put("ICzhou", SMConstants.FLAG_ICI_ZHOU_2008);

        SM_Engine engine_bp = new SM_Engine(graph_BP);
        SM_Engine engine_cc = new SM_Engine(graph_CC);
        SM_Engine engine_mf = new SM_Engine(graph_MF);

        if (components_ssm.length > 2){
            ic = new IC_Conf_Topo(flags_ssm.get(components_ssm[2]));
            if (ic.isCorpusBased()){
                ic = new IC_Conf_Corpus(flags_ssm.get(components_ssm[2]));
            }
            ssm = new SMconf(flags_ssm.get(components_ssm[0]));
            ssm.setICconf(ic);
            aggregation = new SMconf(flags_ssm.get(components_ssm[1]));

            String filename_SSM = SSM_file + "/ss_" + SSM + ".txt";
            pairwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_SSM, ssm, aggregation);

        }else{
            ic = new IC_Conf_Topo(flags_ssm.get(components_ssm[1]));
            if (ic.isCorpusBased()){
                ic = new IC_Conf_Corpus(flags_ssm.get(components_ssm[1]));
            }
            ssm = new SMconf(flags_ssm.get(components_ssm[0]));
            ssm.setICconf(ic);
            String filename_SSM = SSM_file + "/ss_" + SSM + ".txt";
            groupwise_measure_file(graph_BP, graph_CC, graph_MF, engine_bp, engine_cc, engine_mf, factory, pairs_prots, filename_SSM, ssm);
        }
    }
}



public class Run_SS_calculation_GO_yourdataset {
    // 5 arguments: args[0], args[1], args[2], args[3], args[4]
    // args[0] - GO ontology file path
    // arg[1] - GO annotations file path in GAF 2.1 version
    // arg[2] - new GO annotations file path in GAF 2.0 version
    // arg[3] - dataset file path with the pairs of proteins. The format of each line of the dataset files is "Prot1  Prot2   Proxy"
    // arg[4] - new semantic similarity file path
    // arg[5] - SSM
    public static void main(String[] args) throws Exception {

        Convert_GAF_versions annot = new Convert_GAF_versions(args[1], args[2]);
        annot.run();

        Calculate_sim_prot datasets;
        if (args.length == 6){
            datasets = new Calculate_sim_prot(args[0], args[2],
                    new String[]{args[4]}, new String[]{args[3]}, args[5]);
        } else{
            datasets = new Calculate_sim_prot(args[0], args[2],
                    new String[]{args[4]}, new String[]{args[3]}, "all");
        }
        datasets.run();
    }
}
