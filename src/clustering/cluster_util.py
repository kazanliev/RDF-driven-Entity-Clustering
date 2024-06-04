import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import rdflib
import json
from collections import OrderedDict
import logging
from src.classes.rdf_graph import RDFGraph

def parse_rdf(input_file):
    """
    Load RDF data from a turtle file and extract a dictionary with subjects and their predicates (candidate descriptions)
    """
    
    g = RDFGraph()
    entity_predicate_dict =  g.entity_predicate_dict(input_file)

    # If the number of entities is less than 2, break the pipeline
    num_entities = len(entity_predicate_dict)
    if num_entities < 2:
        raise ValueError(f"Only {num_entities} entities have been extracted. Clustering will be performed for 2 or more entities.")
    
    return entity_predicate_dict

def save_dendrogram(Z, labels, file_path, similarity_measure, clustering_method, clustering_score, num_clusters=None):
    """_summary_

    Args:
        Z (ndarray): the hierarchical clustering encoded as a linkage matrix.
        labels (list): list of entity labels (URIs)
        file_path (str): destination folder for the dendrogram
        similarity_measure (str): similarity measure 
        clustering_method (str): clustering (linkage) method 
        clustering_score (str): clustering evaluation index (e.g. Silhouette coefficient) 
        num_clusters (int, optional): Number of clusters used to 'cut the line' (cutoff distance) in the dendrogram. If not specified, none.
    """
    # Display last part of the URI
    modified_labels = [label.split('/')[-1] for label in labels]
    plt.figure(figsize=(20, 10))  
    
    # Determine the cutoff distance from num_clusters and draw a line in the dendrogram
    if num_clusters:
        inverse_index = num_clusters - 1 
        cutoff_distance = Z[-inverse_index, 2]  
        plt.axhline(y=cutoff_distance, c='k', lw=1, linestyle='dashed')
    else: 
        cutoff_distance = None  

    dendrogram(Z, labels=modified_labels, leaf_rotation=90, leaf_font_size=3, color_threshold=cutoff_distance)

    plt.title(f'Dendrogram for {clustering_score}, {similarity_measure}, {clustering_method}')
    plt.xlabel('Entities')
    plt.ylabel('Distance')
    plt.savefig(f"{file_path}.svg", format='svg')  
    # uncomment for saving as png
    # plt.savefig(f"{file_path}.png")
    plt.close()
    # print(f"[INFO] Dendrogram for {clustering_score}, {similarity_measure}, {clustering_method} saved")


def save_clusters_to_json(cluster_labels, subjects, file_path):
    """
    Save the clusters to a json file.

    Args:
        cluster_labels (ndarray): cluster assignment produced by an fcluster function, 
        e.g. for three clusters and 6 entities it could be [1 2 3 2 1 2]
        subjects (list): ordered list of subjects URIs
        file_path (str): output file destination
    """
    
    cluster_dict = {}

    # will raise error if the length of the cluster labels assignment and subject list are different
    # they must correspond because the list of subjects is ordered and was used for calculating the similarity matrix
    for label, subject in zip(cluster_labels, subjects, strict = True):
        subject = subject.split('/')[-1]
        label_str = str(label) 
        if label_str not in cluster_dict:
            cluster_dict[label_str] = [subject]
        else:
            cluster_dict[label_str].append(subject)

    # Sort the dictionary (cluster assignment 1, 2 and so on)
    ordered_cluster_dict = OrderedDict(sorted(cluster_dict.items(), key=lambda x: int(x[0])))

    with open(file_path, 'w') as json_file:
        json.dump(ordered_cluster_dict, json_file, indent=4)


