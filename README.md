# The Supervised Semantic Similarity Toolkit

**SS**: Semantic Similarity; **SSM**: Semantic Similarity Measure; **GO**: Gene Ontology; **HPO**: Human Phenotype Ontology; **PPI**: Protein-Protein Interaction; **GP**: Genetic Programming; **LR**: Linear Regression; **XGB**: XGBoost; **RF**: Random Forest; **BR**: Bayesian Ridge; **DT**: Decision Tree; **MLP**: Multilayer Perceptron; **KNN**: K-Nearest Neighbor.


## Pre-requesites
* install python 3.6.8;
* install java JDK 11.0.4;
* install python libraries by running the following command:  ```pip install -r req.txt```.


## The Toolkit

Our toolkit receives a KG and a list of instance pairs with proxy similarity values and is able to: (1) identify the SAs that describe the KG entities (2) compute KG-based similarities according to different SAs and using different SSMs; (3) train supervised ML algorithms to learn a supervised semantic similarity according to the similarity proxy for which we want to tailor the similarity; (4) evaluate the supervised semantic similarity against a set of baselines.
This framework is independent of the SAs, the specific implementation of KG-based similarity and the ML algorithm employed in supervised learning.

<img src="https://github.com/liseda-lab/Supervised-SS/blob/main/Framework.png"/>


## Datasets and Knowledge Graph
The tookit receives a tab-delimited text file with 3 columns: 
* 1st column - Entity 1 Identifier;	 
* 2nd column - Entity 2 Identifier;
* 3rd column - Proxy Similarity. 

Regarding the KG, the toolkit takes as input an ontology file in OWL format and an instance annotation file in 2.0. or 2.1. GAF format or tsv format.
GAF format (http://geneontology.org/docs/go-annotation-file-gaf-format-2.0/). GAFs are tab-delimited plain text files, where each line in the file represents a single association between a entity and a ontology term/class. 


### Biomedical Benchmark Datasets

This toolkit was successfully applied in a set of 21 protein and gene benchmark datasets (PPI-ALL1, PPI-ALL3, PPI-DM1, PPI-DM3, PPI-HS1, PPI-HS3, PPI-SC1, PPI-SC3, PPI-EC1, PPI-EC3, MF-ALL1, MF-ALL3, MF-DM1, MF-DM3, MF-HS1, MF-HS3, MF-SC1, MF-SC3, MF-EC1, MF-EC3, HPO-dataset) of different species for evaluation. The data is in [Data/kgsimDatasets](https://github.com/ritatsousa/Supervised-SS/tree/master/Data/kgsimDatasets) folder. 

In the MF (also called PFAM) datasets, two proxies of protein similarity based on their biological properties were employed: sequence similarity and PFAM similarity.
In PPI protein datasets, two similarity proxies were also employed: sequence similarity and protein-protein interactions. 
For the HPO-dataset, the proxy similarity is based on phenotypic series.

Regarding the semantic aspects, for the protein datasets, we consider the GO aspects as semantic aspects.
For the gene dataset, in addition to the three GO aspects, the similarity is also calculated for the HP phenotypic abnormality subgraph. Therefore, instead of three semantic aspects, we consider four semantic aspects.


## 1. Semantic Aspects Selection 

As default, our toolkit uses subgraphs rooted in the classes at a distance of one from the KG root class or the subgraphs when the KGs have multiple roots as SAs. 
However, SAs can also be manually defined by selecting the root classes that anchor the aspects.


## 2A. Taxonomic Semantic Similarity Computation
For taxonomic semantic similarity calculation, provide:
* A dataset file with the previously described format;
* A ontology file in OWL format;
* A annotations file in 2.0. or 2.1. 

To support SS calculations, SML was employed. The software is available on GitHub (https://github.com/sharispe/slib/tree/dev/slib-sml) under a CeCILL License.
```
The Semantic Measures Library and Toolkit: fast computation of semantic similarity and relatedness using biomedical ontologies
Sébastien Harispe*, Sylvie Ranwez, Stefan Janaqi and Jacky Montmain
Bioinformatics 2014 30(5): 740-742. doi: 10.1093/bioinformatics/btt581
```

In Linux, compile the command:
```
javac -cp ".:./SS_Calculation/jar_files/*" ./SS_Calculation/Run_SS_calculation.java
```
and then run
```
java -cp ".:./SS_Calculation/jar_files/*" SS_Calculation/Run_SS_calculation
```

**NOTE**: To run in Windows, replace ".:." per ".;.".

This command will create, for each dataset, **SS files** (one for each SSM) with the SS between each pair of entities for each semantic aspect using six different SSMs (ResnikMax_ICSeco, ResnikMax_ICResnik, ResnikBMA_ICSeco, ResnikBMA_ICResnik, simGIC_ICSeco, simGIC_ICResnik). The description of this text file is in [SS_Calculation/SS_files/SS_file format_GO.txt](https://github.com/ritatsousa/Supervised-SS/blob/master/SS_Calculation/SS_files/SS_file_format_GO.txt) file. 

The new SS files are placed in [SS_Calculation/SS_files/datasetname](https://github.com/ritatsousa/Supervised-SS/tree/master/SS_Calculation/SS_files) folder.



## 2B. Embedding Semantic Similarity Computation


### 2B.1. RDF2Vec Embeddings Computation
To calculate RDF2Vec embeddings, an RDF2Vec python implementation was used. The implementation is available on GitHub https://github.com/IBCNServices/pyRDF2Vec.
```
RDF2Vec: RDF graph embeddings for data mining
Petara Ristoski and Heiko Paulheim
International Semantic Web Conference, Springer, Cham, 2016 (pp. 498-514)
```

As default, in RDF2Vec, a set of sequences was generated from Weisfeiler-Lehman subtree kernels.
For the Weisfeiler-Lehman algorithm, we use as default walks with depth 8, and we extracted a limited number of 500 random walks for each entity. The corpora of sequences were used to build a Skip-Gram model with the following default parameters: window size=5; number of iterations=10; entity vector size=200.
However, all the parameters can be changed in the beginning of the python file [SS_Embedding_Calculation/run_RDF2VecEmbeddings.py].

Run the command to calculate the embeddings for each protein using rdf2vec implementation:
```
python3 SS_Embedding_Calculation/run_RDF2VecEmbeddings.py
```
For each dataset, this command creates **embedding files** (one for each semantic aspect) and place them in [SS_Embedding_Calculation/Embeddings/datasetname/aspect](https://github.com/ritatsousa/Supervised-SS/tree/master/SS_Embedding_Calculation/Embeddings) folder.
The description of the embedding text file is in [SS_Embedding_Calculation/Embeddings/Embeddings_format.txt](https://github.com/ritatsousa/Supervised-SS/blob/master/SS_Embedding_Calculation/Embeddings/Embeddings_format.txt) file. The filename is in the format “Embeddings_datasetname_skig-gram_wl_aspect.txt”. 


### 2B.2. OpenKE Embeddings Computation
To compute embeddings using popular graph embeddings methods, OpenKE was used. OpenKE is an open-source framework for knowledge embedding organized by THUNLP based on the TensorFlow toolkit. OpenKE provides fast and stable toolkits, including the most popular knowledge representation learning (KRL) methods. More information is available on their website (http://openke.thunlp.org/). The software is available on GitHub (https://github.com/thunlp/OpenKE/tree/OpenKE-Tensorflow1.0) under a MIT License.
```
OpenKE: An Open Toolkit for Knowledge Embedding
Xu Han and Shulin Cao and Xin Lv and Yankai Lin and Zhiyuan Liu and Maosong Sun and Juanzi Li
Proceedings of EMNLP, 2018 (pp. 139-144)
```

**NOTE**: OpenKE is only implemented for Linux system.

The default parameters given by OpenKE are used.
```
python3 SS_Embedding_Calculation/run_OpenKEmodel.py
```

For each dataset, this command creates **embedding files** (one for each semantic aspect) and place them in [SS_Embedding_Calculation/Embeddings/datasetname/aspect](https://github.com/ritatsousa/Supervised-SS/tree/master/SS_Embedding_Calculation/Embeddings) folder.
The description of the embedding text file is in [SS_Embedding_Calculation/Embeddings/Embeddings_format.txt](https://github.com/ritatsousa/Supervised-SS/blob/master/SS_Embedding_Calculation/Embeddings/Embeddings_format.txt) file. The filename is in the format “Embeddings_datasetname_method_aspect.txt”. 



### 2B.3. OWL2Vec* Embeddings Computation

To calculate OWL2Vec* embeddings, it was used the implementation available on GitHub https://github.com/KRR-Oxford/OWL2Vec-Star.
```
OWL2vec*: Embedding of owl ontologies
Jiaoyan Chen et al.
Machine Learning, 110(7), 1813-1845
```

In OWL2Vec*, as default, a set of sequences was generated from Weisfeiler-Lehman subtree kernels.
For the Weisfeiler-Lehman algorithm, we also use as default walks with depth 8, and we extracted a limited number of 500 random walks for each entity. The corpora of sequences were used to build a Skip-Gram model with the following parameters: window size=5; number of iterations=10; entity vector size=200.


### 2B.4. Compute the Embedding Semantic Similarity for each pair

After generating embeddings for each semantic aspect and then calculated the cosine similarity for each pair
in datasets.
Run the command for calculating embedding similarity for each semantic aspect:
```
python3 SS_Embedding_Calculation/run_embedSS_calculation.py
```
For each dataset, this command creates **1 embedding similarity file** and places it in [SS_Embedding_Calculation/Embeddings_SS_files](https://github.com/ritatsousa/Supervised-SS/tree/master/SS_Embedding_Calculation/Embeddings_SS_files) folder.
The filename is in the format "embedss_200_model_datasetname.txt". 
The format of each line of embedding similarity file is "Ent1  Ent2	ES_SA1	ES_SA2	ES_SA3	ES_SA4"; 


## 3. Supervised Similarity Learning
For 10-cross-validation purposes, run the command to split each dataset into ten partitions:
```
python3 Regression/run_make_shuffle_partitions.py
```
This command will create, for each dataset, **10 Partitions files** and place them in [Regression/Results/Datasetname](https://github.com/ritatsousa/Supervised-SS/tree/master/Regression/Results) folder. Each line of these files is an index (corresponding to a pair) of the dataset.

With semantic similarities, run the command:
```
python3 Regression/run_withPartitions.py
```
For running the baselines (static combinations of semantic aspects), run the command:
```
python3 Regression/run_withPartitions.py True
```


## 4. Supervised Similarity Evaluation 
