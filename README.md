# The Supervised Semantic Similarity Toolkit

**SS**: Semantic Similarity; **SSM**: Semantic Similarity Measure; **GO**: Gene Ontology; **HPO**: Human Phenotype Ontology; **PPI**: Protein-Protein Interaction; **GP**: Genetic Programming; **LR**: Linear Regression; **XGB**: XGBoost; **RF**: Random Forest; **BR**: Bayesian Ridge; **DT**: Decision Tree; **MLP**: Multilayer Perceptron; **KNN**: K-Nearest Neighbor.


## Pre-requesites
* install python 3.6.8;
* install java JDK 11.0.4;
* install python libraries by running the following command:  ```pip install -r req.txt```.


## The Toolkit

Our toolkit receives a KG and a list of instance pairs with proxy similarity values and can: (1) identify the SAs that describe the KG entities (2) compute KG-based similarities according to different SAs and using different SSMs; (3) train supervised ML algorithms to learn a supervised semantic similarity according to the similarity proxy for which we want to tailor the similarity; (4) evaluate the supervised semantic similarity against a set of baselines.

<img src="https://github.com/liseda-lab/Supervised-SS/blob/main/Framework.png"/>

This framework is independent of the SAs, the specific implementation of KG-based similarity, and the ML algorithm employed in supervised learning.
The input files, the SAs, the SSMs, and the algorithms to be used must be defined in the [config.py](https://github.com/liseda-lab/Supervised-SS/blob/main/config.py) file.


## Datasets and Knowledge Graph
The tookit receives a tab-delimited text file with 3 columns: 
* 1st column - Entity 1 Identifier;	 
* 2nd column - Entity 2 Identifier;
* 3rd column - Proxy Similarity. 

Regarding the KG, the toolkit takes as input an ontology file in OWL format and an instance annotation file in 2.0. GAF format or tsv format.
GAF format (http://geneontology.org/docs/go-annotation-file-gaf-format-2.0/). GAFs are tab-delimited plain text files, where each line in the file represents a single association between a entity and a ontology term/class. 


### Biomedical Benchmark Datasets

This toolkit was successfully applied in a set of 21 protein and gene benchmark datasets (PPI-ALL1, PPI-ALL3, PPI-DM1, PPI-DM3, PPI-HS1, PPI-HS3, PPI-SC1, PPI-SC3, PPI-EC1, PPI-EC3, MF-ALL1, MF-ALL3, MF-DM1, MF-DM3, MF-HS1, MF-HS3, MF-SC1, MF-SC3, MF-EC1, MF-EC3, HPO-dataset) of different species for evaluation. The data is in [Data/kgsimDatasets](https://github.com/liseda-lab/Supervised-SS/blob/main/Data/kgsimDatasets) folder. 

In the MF (also called PFAM) datasets, two proxies of protein similarity based on their biological properties were employed: sequence similarity and PFAM similarity.
Two similarity proxies were also employed in PPI protein datasets: sequence similarity and protein-protein interactions. 
For the HPO-dataset, the proxy similarity is based on phenotypic series.

Regarding the semantic aspects, we consider the GO aspects as semantic aspects for the protein datasets.
In addition to the three GO aspects, the similarity is also calculated for the HP phenotypic abnormality subgraph for the gene dataset. Therefore, instead of three semantic aspects, we consider four semantic aspects.


## 1. Semantic Aspects Selection 

By default, our toolkit uses subgraphs rooted in the classes at a distance of one from the KG root class or the subgraphs when the KGs have multiple roots as SAs. 
However, SAs can also be manually defined by selecting the root classes that anchor the aspects.

If the SAs are not given manually, run the command:
```
python3 SA_Selection/run_SAs_selection.py
```

## 2. Taxonomic Semantic Similarity Computation
For semantic similarity calculation, provide:
* A dataset file with the previously described format;
* A ontology file in OWL format;
* A annotations file in 2.0. or 2.1. 

To run, compile the command:
```
python3 SS_Calculation/run_SS_calculation_SAs.py
```

For a taxonomic SSM this command will create, a **SS file** with the SS between each pair of entities for each semantic aspect using the defined SSM. The description of this text file is [here](https://github.com/liseda-lab/Supervised-SS/blob/main/SS_Calculation/SS_files/SS_file_format_GO.txt). 

For a embedding-based SSM, this command creates a **embedding SS file**. The description of this text file is [here](https://github.com/liseda-lab/Supervised-SS/blob/main/SS_Calculation/Embeddings_SS_files/SS_file_format_GO.txt). 
In addition to the SS file, it creates **embedding files** (one for each semantic aspect).
The description of the embedding text file is [here](https://github.com/liseda-lab/Supervised-SS/blob/main/SS_Calculation/Embeddings/Embeddings_format.txt).


### 2.1. Taxonomic Semantic Similarity
To support SS calculations, SML was employed. The software is available on [GitHub](https://github.com/sharispe/slib/tree/dev/slib-sml) under a CeCILL License.
```
The Semantic Measures Library and Toolkit: fast computation of semantic similarity and relatedness using biomedical ontologies
Sébastien Harispe*, Sylvie Ranwez, Stefan Janaqi and Jacky Montmain
Bioinformatics 2014 30(5): 740-742. doi: 10.1093/bioinformatics/btt581
```

### 2.2. RDF2Vec Embeddings Semantic Similarity
To calculate RDF2Vec embeddings, an [RDF2Vec python implementation](https://github.com/IBCNServices/pyRDF2Vec) was used.
```
RDF2Vec: RDF graph embeddings for data mining
Petara Ristoski and Heiko Paulheim
International Semantic Web Conference, Springer, Cham, 2016 (pp. 498-514)
```

As default, in RDF2Vec, a set of sequences was generated from Weisfeiler-Lehman subtree kernels.
For the Weisfeiler-Lehman algorithm, we use as default walks with depth 8, and we extracted a limited number of 500 random walks for each entity. The corpora of sequences were used to build a Skip-Gram model with the following default parameters: window size=5; number of iterations=10; entity vector size=200.
However, all the parameters can be changed in the beginning of the [python file](https://github.com/liseda-lab/Supervised-SS/blob/main/SS_Calculation/run_RDF2VecEmbeddings.py).


### 2.3. OWL2Vec* Embeddings Semantic Similarity

To calculate OWL2Vec* embeddings, it was used the implementation available on [GitHub](https://github.com/KRR-Oxford/OWL2Vec-Star).
```
OWL2vec*: Embedding of owl ontologies
Jiaoyan Chen et al.
Machine Learning, 110(7), 1813-1845
```

In OWL2Vec*, as default, a set of sequences was generated from Weisfeiler-Lehman subtree kernels.
For the Weisfeiler-Lehman algorithm, we also use as default walks with depth 8, and we extracted a limited number of 500 random walks for each entity. The corpora of sequences were used to build a Skip-Gram model with the following parameters: window size=5; number of iterations=10; entity vector size=200.
However, all the parameters can be changed in the beginning of the [python file](https://github.com/liseda-lab/Supervised-SS/blob/main/SS_Calculation/run_OWL2VecEmbeddings.py).


### 2.4. OpenKE Embeddings Semantic Similarity
To compute embeddings using popular graph embeddings methods, OpenKE was used. OpenKE is an open-source framework for knowledge embedding organized by THUNLP based on the TensorFlow toolkit. OpenKE provides fast and stable toolkits, including the most popular knowledge representation learning (KRL) methods. More information is available on their [website](http://openke.thunlp.org/). The software is available on [GitHub](https://github.com/thunlp/OpenKE/tree/OpenKE-Tensorflow1.0) under a MIT License.
```
OpenKE: An Open Toolkit for Knowledge Embedding
Xu Han and Shulin Cao and Xin Lv and Yankai Lin and Zhiyuan Liu and Maosong Sun and Juanzi Li
Proceedings of EMNLP, 2018 (pp. 139-144)
```

**NOTE**: OpenKE is only implemented for Linux system.

The default parameters given by OpenKE are used.



## 3. Supervised Similarity Learning

To train a supervised semantic similarity according to the similarity proxy, eight representative ML algorithms for regression can be employed: LR, BR, KNN, GP, DT, MLP, RF, XGB. 
Except for GP, XGB and RF, the default parameters are the default scikit-learn values. 
For running GP, we use [gplearn 3.0](https://gplearn.readthedocs.io/en/stable/), a freely available package that runs with the scikit-learn library with the parameters:

Parameter | Value
------------- | -------------
Population size | 500
Number of generations | 50
Fitness Function | RMSE
Tournament size | 20
Stopping criteria | 0.0
Range of constants to include in formulas | [-1.0,1.0]
Range of tree depths for the initial population | [2,6]
Initialization method | half and half
Probability of crossover on a tournament winner | 0.9
Probability of subtree mutation on a tournament winner | 0.01
Probability of hoist mutation on a tournament winner | 0.01
Probability of point mutation on a tournament winner | 0.01
Probability of any given node will be mutated, for point mutation | 0.05

For XGB, we use the [XGBoost 1.1.1 package](https://xgboost.readthedocs.io), with the values of some parameters altered to maximize the performance of the model, through grid search. 

Parameter | Value
------------- | -------------
Maximum depth | 2,4,6
Number of estimators |  50,100,200
Learning rate | 0.1, 0.01, 0.001
        
For RF, using scikit-learn, we also optimize some parameters:

Parameter | Value
------------- | -------------
Maximum depth | 2,4,6, None
Number of estimators |  50,100,200      

For 10-cross-validation purposes, run the command to split each dataset into ten partitions:
```
python3 Regression/run_make_shuffle_partitions.py
```
This command will create, for each dataset, **10 Partitions files**. Each line of these files is an index (corresponding to a pair) of the dataset.

With semantic similarities, run the command:
```
python3 Regression/run_withPartitions.py
```


## 4. Supervised Similarity Evaluation 

We compute the static similarity for each semantic aspect and use, as baselines, the single aspect similarities and two well-known strategies for combining the single aspect scores, the average and maximum.

For running the baselines (static combinations of semantic aspects), run the command:
```
python3 Regression/run_baselines.py
```
