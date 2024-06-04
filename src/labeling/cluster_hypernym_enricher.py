import pandas as pd
import json
import os

def cluster_hypernym_enricher(csv_hypernym_dictionary, clustering_file_path, output_file_path):
    """
    Assigns a DBpedia hypernym (gold:hypernym) to each entity in the input set of clusters (clustering).

    Args:
        csv_hypernym_dictionary (str): file path of the hypenym dictionary [Entity, DBpedia Hypernym] 
        clustering_file_path (str): file path of the clustering for which elements we want to extract corresponding hypenyms
        output_file_path (str): destination file path for clustering with assigned hypernyms
    """

    # Process hypernym dictionary
    hypernyms_df = pd.read_csv(csv_hypernym_dictionary)
    hypernym_dict = pd.Series(hypernyms_df.Hypernym.values, index=hypernyms_df.Entity).to_dict()

    # Process clustering
    with open(clustering_file_path, 'r') as file:
        clusters = json.load(file)

    # Enrich the clusters with hypernyms from the dictionary, 'Not found' for DBpedia entities
    # that do not have gold:hypernym
    enriched_clusters = {}
    for cluster_id, entities in clusters.items():
        enriched_entities = {entity: hypernym_dict.get(entity, 'Not found') for entity in entities}
        enriched_clusters[cluster_id] = enriched_entities

    with open(output_file_path, 'w') as file:
        json.dump(enriched_clusters, file, indent=4)

    # print(f"[INFO] Enriched clusters saved to {output_file_path}")
    

def hypernym_enricher_folder(csv_hypernym_dictionary, input_folder_path, output_folder_path):
    """
    Process all files in the input folder with the cluster_hypernym_enricher function.
    
    Args:
      csv_hypernym_dictionary (str): file path of the hypenym dictionary [Entity, DBpedia Hypernym] 
      input_folder_path (str): path to the input folder containing clusterings (JSON files).
      output_folder_path (str): path to the output folder where enriched clustering will be saved.
    """

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
    for filename in os.listdir(input_folder_path):
        input_file_path = os.path.join(input_folder_path, filename)
        output_file_path = os.path.join(output_folder_path, filename)
        
        if os.path.isfile(input_file_path):
            cluster_hypernym_enricher(csv_hypernym_dictionary, input_file_path, output_file_path)

    print(f"[INFO] Added hypernyms to clusterings from {input_folder_path} and saved to {output_folder_path}")
