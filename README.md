# RDF-driven Entity Clustering of Unstructured Data

## Overview

We present an RDF-driven Entity Clustering pipeline for text (.txt) files, utilizing a hierarchical clustering algorithm as presented in the works of Christodoulou et al. [[1]](#1) and Eddamiri et al. [[2]](#2). Our pipeline uses DBpedia[[3]](#3) for further knowledge extraction and builds up on Natural Language Processing tools, including REBEL [[4]](#4) for relational triple extraction and spaCy [[5]](#5) for Named Entity Recognition.

## Compatibility

The pipeline has been tested on the following Ubuntu LTS versions:

- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS


## Installation

1. **Clone the Project**

2. **Update System Packages and Check Python Version**

```bash
sudo apt update
sudo apt upgrade
```
```bash
python3 --version

```
Make sure that you have Python3.10.12 or >= Python3.10.14

3. **Install Python 3.10 (if needed)**
   
Add the deadsnakes PPA repository:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```
Install Python 3.10, GCC and dev package:
```bash 
sudo apt update
sudo apt install python3.10 python3.10-dev
```

```bash
sudo apt-get install gcc python3.10-dev
```
```bash
python3.10 --version 
```
If your Python version is 3.10.12 or greater than or equal to 3.10.14, proceed to the next step.

4. **Create and Activate Virtual Environment**
   
Install the Python 3.10 virtual environment package:
```bash
sudo apt install python3.10-venv -y
```
Create a virtual environment in the project repository and activate it:
```bash
python3.10 -m venv myenv
source myenv/bin/activate
pip install --upgrade pip # upgrade pip in myenv
```

5. **Install Reqirements**
```bash
pip install -r requirements.txt
```
**Note:** Approximately 6 GB of free space is needed to install the requirements.

## Usage
To run the pipeline, execute the following command:

```bash
python pipeline.py
```
You will be prompted further to specify an input file and output folder path.

## Project Structure
The project has the following structure:
```
RDF-driven-Entity-Clustering/
│
├── input/                      # Contains example texts as input for the pipeline
├── logs/                       # Folder to save log files
├── reports/                    # Folder to save manual clustering evaluations
├── resources/                  # Contains file constants used in the pipeline
├── results/                    # Output folder to save results
├── src/                        # Contains the source code subdirectories:
│   ├── clustering/             # Python scripts that perform hierarchical clustering
│   ├── clustering_prep/        # Scripts preparing REBEL and DBpedia triples for clustering
│   ├── evaluation_prep/        # Scripts extracting information for manual cluster evaluation
│   ├── gen_resources/          # Scripts for generating constant file resources
│   ├── labeling/               # Scripts for hypernym labeling of elements and clusters
│   ├── rebel_extraction/       # Scripts for triples extraction with REBEL
│   ├── spacy_dbpedia_extraction/  # Scripts for triples extraction from DBpedia after NER with spaCy
│   └── util/                   # Utility scripts for the pipeline
├── evaluator.py                # Script to facilitate manual evaluation of clusters 
└── pipeline.py                 # Main pipeline script

```

## Output Folder Structure

The result output folder after will contain the following structure after running the pipeline:
```
{input_file_name}/
├── 1_text_chunks/                       # Text chunks of the input file to be processed by REBEL
├── 2_result_clusters/                   # Cluster sets with unlabeled entity clusters and entities
├── 3_clusters_with_hypernyms/           # Cluster sets with entities labeled with DBpedia gold:hypernym property
├── 4_labeled_clusters/                  # Cluster sets with cluster labels based on the hypernyms of the elements
├── 5_labeled_clusters_dcterms_rdf/      # Labeled clusters with extracted rdf:type and dcterms:subject DBpedia properties to facilitate manual evaluation
├── 6_result_clusters_dendrograms/       # Dendrograms corresponding to the clusterings
├── 7_dcterms_rdf_prop_graphs/           # Turtle files containing rdf:type and dcterms:subject DBpedia properties for each extracted entity
├── 1.1_REBEL_triples_{input_file_name}.ttl         # Triples extracted with REBEL
├── 1.2_REBEL_linked_triples_{input_file_name}.ttl  # REBEL triples with subjects linked to DBpedia URIs
├── 2.1_spacy_entities_linked_{input_file_name}.csv # Entities extracted with spaCy and linked to DBpedia URIs
├── 2.2_spacy_entity_properties_{input_file_name}.ttl # DBpedia triples for the extracted spaCy entities + REBEL subjects (entities)
├── 3_combined_triples_{input_file_name}.ttl        # Union of triples from 2.2 and 1.2
├── 4_combined_entities_{input_file_name}.csv       # List of all entities linked to DBpedia URIs
├── 5_hypernym_dict_{input_file_name}.csv           # For each entity, its corresponding gold:hypernym value from DBpedia
└── 6_statistics_{input_file_name}.txt              # Statistics file generated after running the pipeline
```

**Note:** For instructions on how to evaluate the output, refer to the `evaluator.py` script.

## References

<a id="1">[1]</a>: Christodoulou, K., Paton, N. W., & Fernandes, A. A. A. (2015). Structure inference for linked data sources using clustering. Lecture Notes in Computer Science (Including Subseries Lecture Notes in Artificial Intelligence and Lecture Notes in Bioinformatics), 8990. https://doi.org/10.1007/978-3-662-46562-2_1

<a id="2">[2]</a>: Eddamiri, S., Zemmouri, E. M., & Benghabrit, A. (2019). An improved RDF data Clustering Algorithm. Procedia Computer Science, 148. https://doi.org/10.1016/j.procs.2019.01.038

<a id="3">[3]</a>: https://www.dbpedia.org/

<a id="4">[4]</a>: [REBEL GitHub Repository](https://github.com/Babelscape/rebel)

<a id="5">[5]</a>: [spaCy GitHub Repository](https://github.com/explosion/spaCy)
