import json
from collections import Counter
import os

def assign_labels_to_clusters_with_global_counts(enriched_clusters_file, hypernyms_counts_file, output_file_path):
    """
    Assign labels to clusters based on the most common hypernym in each cluster. In case of a tie, 
    use the hypernym with the highest global usage count as a label. 

    Args:
      enriched_clusters_file (str): path to a clustering (with corresponding hypernym valies for each entity)
      hypernyms_counts_file (str): path to the file with global usage counts of hypenyms (we use 'resources/dbpedia_hypernyms').
      output_file_path (str): destination file path for the named clustering.
    """

    # Load clustering and hypernym counts file
    with open(enriched_clusters_file, 'r') as file:
        clusters = json.load(file)

    with open(hypernyms_counts_file, 'r') as file:
        hypernyms_counts = json.load(file)
    hypernym_global_counts = {item['hypernym']: item['count'] for item in hypernyms_counts}

    labeled_clusters = {}
    label_counts = {}
    for cluster_id, entities in clusters.items():
        hypernyms = [hypernym for hypernym in entities.values() if hypernym != "Not found"]
        if hypernyms:
            # find the most common hypernym(s)
            # if there is a tie, then resolve by choosing the hypenym
            # that is most commonly used in DBpedia (counts extracted in a resource file)
            hypernym_counts = Counter(hypernyms)
            max_count = hypernym_counts.most_common(1)[0][1]
            candidates = [hypernym for hypernym, count in hypernym_counts.items() if count == max_count]
            selected_hypernym = max(candidates, key=lambda x: hypernym_global_counts.get(x, 0)) if candidates else "Miscellaneous Cluster"
        else:
            selected_hypernym = "Miscellaneous Cluster"

        # Ensure unique keys by appending a count to the label
        # We also want to easily track the number of clusters 
        # labeled with the same hypenym
        label_count = label_counts.get(selected_hypernym, 0) + 1
        label_counts[selected_hypernym] = label_count
        unique_label = f"{selected_hypernym} {label_count}"
        labeled_clusters[unique_label] = entities

    # Save labeled clusters
    with open(output_file_path, 'w') as file:
        json.dump(labeled_clusters, file, indent=4)

def assign_label_to_clusters_folder(input_folder_path, output_folder_path, hypernyms_counts_file):
    """
    Label all clusterings in the input folder applying with a hypenym.
    
    Args:
      input_folder_path (str): path to the input folder containing clusterings with hypenym labeled entities
      output_folder_path (str): path to the output folder where clustering with labels for each cluster will be saved.
      hypernyms_counts_file (str): path to a file constant which contains DBpedia hypenyms and their global occurence counts.
    """
    
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
    for filename in os.listdir(input_folder_path):
        input_file_path = os.path.join(input_folder_path, filename)
        output_file_path = os.path.join(output_folder_path, filename)
        
        if os.path.isfile(input_file_path):
            assign_labels_to_clusters_with_global_counts(input_file_path, hypernyms_counts_file, output_file_path)

    print(f"[INFO] Assigned hypenym labels for each entity to clusterings from {input_folder_path} and saved to {output_folder_path}")
