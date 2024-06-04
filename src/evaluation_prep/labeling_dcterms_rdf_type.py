import json
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import os
from src.classes.rdf_graph import RDFGraph

def count_additional_property_values(entities, rdf_type_dict, dcterms_subject_dict):
    """
    Fetch values of 'rdf:type' and 'dcterms:subject' for the specified list of entities
    and for each value count how many of the entities are associated with it.
    """
    subjects_counter = Counter()
    types_counter = Counter()

    subjects = {}
    types = {}
    for entity in entities:
        entity_url = f'http://dbpedia.org/resource/{entity}'
        if entity_url in dcterms_subject_dict:
            subjects = dcterms_subject_dict[entity_url]
        if entity_url in rdf_type_dict:
            types = rdf_type_dict[entity_url]
        subjects_counter.update(subjects)
        types_counter.update(types)

    return subjects_counter, types_counter

def sort_label_data(counter, entity_count):
    """
    Sort the extracted values for 'rdf:type' and 'dcterms:subject' in desc order of frequency for a given cluster.
    Also discard the values which apply to less than 50% of the cluster elements.
    """
    threshold = entity_count / 2
    sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return {item.split('/')[-1].replace('_', ' '): count for item, count in sorted_items if count >= threshold}

def process_clusters_label_dcterms_rdf(json_file, output_file, rdf_type_dict, dcterms_subject_dict):
    """
    Save dcterms:subject and rdf:type values applying to more than 50% of the entities of each clustering.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)

    updated_data = {}
    for cluster_name, entities_info in data.items():
        entities = list(entities_info.keys())
        entity_count = len(entities) 
        subjects_counter, types_counter = count_additional_property_values(entities, rdf_type_dict, dcterms_subject_dict)
    
        subjects_data = sort_label_data(subjects_counter, entity_count)
        types_data = sort_label_data(types_counter, entity_count)
        
        if entity_count == 1:
            updated_data[cluster_name] = {
            "entities": entities_info
            }
        else: 
            updated_data[cluster_name] = {
            "entities": entities_info,
            "dcterms:subject_values": subjects_data,
            "rdf:type_values": types_data
        }  

    # Save 
    with open(output_file, 'w') as file:
        json.dump(updated_data, file, indent=4, ensure_ascii=False)

    return updated_data

def process_clusters_label_dcterms_rdf_folder(input_folder_path, output_folder_path, dcterms_rdf_file_base):
    """
    Process all files in the input folder applying the process_clusters_label_dcterms_rdf function.
    Generates a clustering with additional information ('dcterms:subject' and 'rdf:type' values for 
    entities of each cluster) that can be helpful for rating the clustering manually.
    
    Args:
        input_folder_path (str): path to the labeled clusterings.
        output_folder_path (str): output folder path for the clusterings enriched with additional info
        dcterms_rdf_file_base (str): output folder path for separately saving dcterms:subject and rdf:type
        values for each subject as predicates in relational triples
    """

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    rdf_type_file = f'{dcterms_rdf_file_base}_rdf_type.ttl'
    dcterms_subject_file = f'{dcterms_rdf_file_base}_dcterms_subject.ttl'

    g_rdf_type = RDFGraph()
    g_dcterms_subject = RDFGraph()

    rdf_type_dict = g_rdf_type.entity_predicate_dict(rdf_type_file)
    dcterms_subject_dict = g_dcterms_subject.entity_predicate_dict(dcterms_subject_file)


    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder_path):
        input_file_path = os.path.join(input_folder_path, filename)
        output_file_path = os.path.join(output_folder_path, filename)
        
        if os.path.isfile(input_file_path):
            process_clusters_label_dcterms_rdf(input_file_path, output_file_path, rdf_type_dict, dcterms_subject_dict)
    print(f"[INFO] Added dcterms:subject and rdf:type summaries for clusterings in {input_folder_path} and saved the output to {output_folder_path}")
