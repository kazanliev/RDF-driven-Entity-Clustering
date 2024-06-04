"""
Evaluator for clustering summaries (containing values for the rdf:type and dcterms:subject DBpedia properties
which apply to the majority of the entities in every cluster).

Generates a report file with the cluster evaluation and values for the evaluation metrics and saves it in the report folder.

How to use:

    1. Save the path of a given clustering from the "5_labeled_clusters_dcterms_rdf" folder to the INPUT_FILE constant.

    2. You can also change the output folder ('REPORT_FOLDER' constant), the default folder is "reports".

    3. Run

    4. Follow the prompts to evaluate each cluster:

    (Note: displayed labels are NOT official labels of the clusters and the displayed values of rdf:type and dcterms:subject can 
    help you in the evaluation process. For instance, if you see that 40 out of 50 entities have a type of politician, you can
    assume that at least 40 out of 50 are really politicians, or, e.g., in the following cluster:

        Cluster: Company 1
            -1- Adidas: Corporation              URL: <http://dbpedia.org/resource/Adidas>
            -2- Deutsche_Telekom: Company              URL: <http://dbpedia.org/resource/Deutsche_Telekom>
            -3- Robert_Bosch_GmbH: Engineering              URL: <http://dbpedia.org/resource/Robert_Bosch_GmbH>
            dcterms:subject_values:
                Category:Multinational companies headquartered in Germany: 3
                ...

    we get a really good recommendation: "Category:Multinational companies headquartered in Germany: 3" with '3' meaning all three elements
    have this property)

        4.1. Evaluate a cluster as accurate (type 'accurate') if you can think of a cluster label
            that would be accurate for all entities and not too general
            (e.g., "humans" would be a broad label in the context of longer texts,
            look for more specific cluster labels, e.g., (at least as specific as) "politicians", "universities", "cities" etc.)

        4.2. Evaluate a cluster as 'inaccurate' you cannot think of an accurate cluster label for the cluster.

        4.3. Pass a cluster (type 'p') if you want to exclude a cluster from the evaluation.
             For example, in our research we used this option to one-element clusters.

        4.4. Evaluater a cluster as 'partly accurate' if you can think of a good label that would describe
            at least half of the elements, but not all of them. Then you would be prompted further to evaluate each element:

             4.4.1. type 1 and enter, if you think the element is accurately placed in the cluster based on your label.

             4.4.2. type 0 otherwise.

    5. After all clusters have been evaluated, a report is automatically saved to the OUTPUT_FOLDER. 

    NOTE: In 'partly accurate' clusters we did not evaluate each entity separately. In case that N out of M entities are put in an
    accurate category,e.g, 'Politician' from rdf:type, we would evaluate the first N as 1 (accurate) and the rest as inaccurate 
    (or the first M-N as 0 and the rest as 1).
"""
import json
import os
from datetime import datetime

INPUT_FILE = "Germany/5_labeled_clusters_dctemrs_rdf/clusters_Germany_Silhouette_sorensen_weighted.json"
OUTPUT_FOLDER = "reports"

def ask_user_about_cluster(cluster_name, cluster_info, skip_with_enter):
    """
    Display all elements of the currently evaluated clusters and process the user input.
    """

    #Display all entities in the current cluster
    print(f"\nCluster: {cluster_name}")
    entities = cluster_info['entities']

    for index, (entity, label) in enumerate(entities.items(), start=1):
        print(f"-{index}- {entity}: {label}              URL: <http://dbpedia.org/resource/{entity}>")
    
    #Display the corresponding values for "dcterms:subject" that apply for at least 1/2 of the entities
    print("dcterms:subject_values:")
    for subject, count in cluster_info.get('dcterms:subject_values', {}).items():
        print(f"  {subject}: {count}")
    
    #Display the corresponding values for "rdf:type" that apply for at least 1/2 of the entities
    print("rdf:type_values:")
    for type_label, count in cluster_info.get('rdf:type_values', {}).items():
        print(f"  {type_label}: {count}")
    
    response = input("Evaluate this cluster as 'accurate', 'partly accurate', 'inaccurate' ('p' to ignore the cluster)? ").lower()

    if response == 'p': 
        return None, None, True  # True means this cluster was ignored ('p')
    elif response == '' and skip_with_enter==True:
        return None, None, True #cluster can be directly skipped with enter
    elif response == '' and skip_with_enter==False:
        print("Cluster cannot be skipped.")
        return ask_user_about_cluster(cluster_name, cluster_info, skip_with_enter)
    elif response in ['accurate', 'partly accurate', 'inaccurate']: #cluster evaluated
        accuracy, validated_entities = process_cluster_accuracy(entities, response)
        return accuracy, validated_entities, False
    else:
        print("Unexpected input. Please re-enter.")
        return ask_user_about_cluster(cluster_name, cluster_info, skip_with_enter)

def process_cluster_accuracy(entities, response):
    """
    Processes the user input if the cluster is being evaluated (not ignored).
    Returns an accuracy value of 1, if the cluster is labeled as 'accurate' or
    'partly accurate', and a value of 0 if it is labeled as 'inaccurate'. 

    Returns:
        accuracy: value of 1, if the cluster is labeled as 'accurate' or 
        'partly accurate', and a value of 0 if it is labeled as 'inaccurate'. 
        validated_entities:  0/1 for each entity, if 'inaccurate'/'accurate',
        if 'partly accurate' 0 or 1 or each entity depending on the user input.
    """
    accuracy = None
    validated_entities = {}
    if response == 'partly accurate':
        accuracy = 1
        for entity in entities.keys():
            while True:
                try:
                    #Ask user to evaluate each entity separately as 'accurate' or 'inaccurate'
                    entity_accuracy = input(f"Is {entity} 'accurate' (1) or 'inaccurate' (0)? ")
                    if entity_accuracy not in ["1", "0"]:
                        raise ValueError("Input must be '1' for accurate or '0' for inaccurate.")
                    validated_entities[entity] = int(entity_accuracy)
                    break
                except ValueError as e:
                    print(e)
    elif response == 'accurate':
        accuracy = 1
        validated_entities = {entity: 1 for entity in entities.keys()}
    elif response == 'inaccurate':
        accuracy = 0
        validated_entities = {entity: 0 for entity in entities.keys()}
    return accuracy, validated_entities

def generate_report_filename(input_filepath, base_folder):
    """
    Helper function to generate a unique name for the evaluation report with a date string
    """
    base_name = os.path.basename(input_filepath)
    name_without_ext = os.path.splitext(base_name)[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return os.path.join(base_folder, f"{name_without_ext}_{timestamp}.txt")

def save_report(filepath, content):
    """
    Helper function to save the report
    """
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath, 'w') as file:
        file.write(content)

def calculate_performance_measures(validated_clusters):
    """
    Processes the evaluation of each cluster (except for the excluded (passed) ones).

    Returns:
        cm_overall: Coherence Measure
        pm: Precision Measure
        ccm: Clusters Coherence Measure
    """
    #Total number of entities that have been included in the evaluation
    evaluated_entities = sum(len(entities) for entities in validated_clusters.values())

    #Total number of entities evaluated as accurately placed in their corresponding clusters
    relevant_entities = sum(sum(entities.values()) for entities in validated_clusters.values())

    total_number_of_clusters = len(validated_clusters)

    if total_number_of_clusters == 0:  # Avoid division by zero
        return 0, 0, 0

    # Calculate accurate clusters: those with any entities marked as accurately placed
    accurate_clusters = sum(1 for entities in validated_clusters.values() if any(value == 1 for value in entities.values()))

    # Coherence Measure 
    cm_overall = sum(sum(entities.values())/len(entities) for entities in validated_clusters.values()) / total_number_of_clusters
    
    # Precision Measure
    pm = relevant_entities / evaluated_entities if evaluated_entities > 0 else 0

    # Coherent Clusters Measure
    ccm = accurate_clusters / total_number_of_clusters

    return cm_overall, pm, ccm

def main():
    # Load clustering file
    filepath = INPUT_FILE 
    with open(filepath, 'r') as file:
        clusters = json.load(file)

    cluster_accuracies = []
    validated_clusters = {}
    passed_clusters = []

    #Process user input
    for cluster_name, cluster_info in clusters.items():
        entities_length = len(cluster_info['entities'].items())
        # if there is only one entity in the cluster, 
        # we want to allow excluding the entity by pressing enter
        if entities_length==1:
            skip_with_enter = True
        else:
            skip_with_enter = False
        accuracy, validated_entities, is_passed = ask_user_about_cluster(cluster_name, cluster_info, skip_with_enter)
        if is_passed:
            passed_clusters.append(cluster_name)
            continue
        validated_clusters[cluster_name] = validated_entities
        cluster_accuracies.append(accuracy)

    total_entities = sum(len(entities) for entities in validated_clusters.values())
    relevant_entities = sum(sum(entities.values()) for entities in validated_clusters.values())
    accurate_clusters = sum(cluster_accuracies)  
    total_number_of_clusters = len(validated_clusters)+len(passed_clusters)
    num_validated_clusters = len(validated_clusters)

    # Save the report
    # Report folder - can be changed
    report_folder = OUTPUT_FOLDER 
    report_filepath = generate_report_filename(filepath, report_folder)
    report_content = "Summary of Clustering Evaluation\n\n"
    report_content += f"Total number of clusters: {total_number_of_clusters}\n"
    report_content += f"Number of evaluated clusters: {num_validated_clusters}\n"
    report_content += f"Number of excluded (one-element) clusters: {len(passed_clusters)}\n"
    report_content += f"Number of entities in the evaluated clusters: {total_entities}\n"
    report_content += f"Number of accurately placed entities in the evaluated clusters: {relevant_entities}\n"
    report_content += f"Number of accurate clusters in the evaluated clusters: {accurate_clusters}\n\n"
    


    if validated_clusters:
        cm_overall, pm, ccm = calculate_performance_measures(validated_clusters)
        report_content += f"\nCoherence Measure: {cm_overall}\n"
        report_content += f"Precision Measure: {pm}\n"
        report_content += f"Coherent Clusters Measure: {ccm}\n"
        report_content += f"Precision Measure x (Evaluated clusters/Clusters): {pm*(num_validated_clusters/total_number_of_clusters)}\n\n"
    else:
        report_content += "\nNo clusters were evaluated for performance measures.\n"

    # Ignored clusters
    report_content += "Ignored clusters:\n"
    if passed_clusters:
        for cluster in passed_clusters:
            report_content += f"- {cluster}\n"
    else:
        report_content += "No clusters were passed.\n"

    # Evaluated clusters
    report_content += "\nEvaluated Clusters:\n"
    for cluster_name, entities in validated_clusters.items():
        report_content += f"\nCluster: {cluster_name}\n"
        for entity, accuracy in entities.items():
            report_content += f"- {entity}: {'1 (accurately placed)' if accuracy == 1 else '0' }\n"


    save_report(report_filepath, report_content)
    print(f"[INFO] Evaluation report saved to {report_filepath}")

if __name__ == '__main__':
    main()