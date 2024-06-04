"""
Contains utility functions and constants to set up and run the main pipeline.
"""

import os
import datetime
import logging

LOG_FOLDER = 'logs'

#subfolders in the destination output folder
OUTPUT_FOLDERS = [
        "1_text_chunks", 
        "2_result_clusters", 
        "3_clusters_with_hypernyms", 
        "4_labeled_clusters", 
        "5_labeled_clusters_dctemrs_rdf", 
        "6_result_clusters_dendrograms", 
        "7_dcterms_rdf_prop_graphs"
    ]

def get_timestamp():
    """
    Return timestamp
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_paths(output_folder, base_name):
    """
    Generate names and prefixes for files used in the pipeline.
    """
    paths = {
        "text_chunks": f'{output_folder}/{base_name}/1_text_chunks',
        "REBEL_triples": f'{output_folder}/{base_name}/1.1_REBEL_triples_{base_name}.ttl',
        "REBEL_linked_triples": f'{output_folder}/{base_name}/1.2_REBEL_linked_triples_{base_name}.ttl',
        "spacy_linked_entities": f'{output_folder}/{base_name}/2.1_spacy_entities_linked_{base_name}.csv',
        "spacy_entity_properties": f'{output_folder}/{base_name}/2.2_spacy_entity_properties_{base_name}.ttl',
        "combined_triples": f'{output_folder}/{base_name}/3_combined_triples_{base_name}.ttl',
        "combined_entities": f'{output_folder}/{base_name}/4_combined_entities_{base_name}.csv',
        "hypernym_dict": f'{output_folder}/{base_name}/5_hypernym_dict_{base_name}.csv',
        "statistics": f'{output_folder}/{base_name}/6_statistics_{base_name}.txt',
        "result_clusters": f'{output_folder}/{base_name}/2_result_clusters',
        "clustering_output_base": f'{output_folder}/{base_name}/2_result_clusters/clusters_{base_name}',
        "clusters_with_hypernyms": f'{output_folder}/{base_name}/3_clusters_with_hypernyms',
        "labeled_clusters": f'{output_folder}/{base_name}/4_labeled_clusters',
        "labeled_clusters_dcterms_rdf": f'{output_folder}/{base_name}/5_labeled_clusters_dctemrs_rdf',
        "dendrograms_base": f'{output_folder}/{base_name}/6_result_clusters_dendrograms/dendro_{base_name}',
        "dcterms_rdf_prop_base": f'{output_folder}/{base_name}/7_dcterms_rdf_prop_graphs/{base_name}_additional'
    }
    return paths

def setup_logging(article_name):
    """
    Set up logging for main
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    base_name = os.path.splitext(os.path.basename(article_name))[0]

    start_time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"{LOG_FOLDER}/log_{base_name}_{start_time_str}.txt"

    # Create logger
    logger = logging.getLogger(article_name)
    logger.setLevel(logging.INFO) 
    file_handler = logging.FileHandler(log_file_name)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_start_end(logger, process_name, article_name, process_func):
    """
    Helper function to log the begin and end time for the pipeline steps that usually take longer
    """
    logger.info(f"{process_name} for {article_name} started at {get_timestamp()}")
    start = datetime.datetime.now()
    result = process_func()
    end = datetime.datetime.now()
    logger.info(f"{process_name} for {article_name} ended at {get_timestamp()}")
    logger.info(f"{process_name} for {article_name} took {(end - start).total_seconds()} seconds")
    return result


def prompt_user_input(function):
    """
    Prompt the user to specify input file and destination folder before running the pipeline
    """
    # input folder prompt
    while True:
        input_file_path = input("Please enter the path to the input text file: ")
        if os.path.isfile(input_file_path) and input_file_path.lower().endswith('.txt'):
            break
        elif not os.path.isfile(input_file_path):
            print("Invalid input. Input file does not exist.")
        else:
            print("Invalid input. Please select a text (.txt) file.")

    # output folder prompt
    while True:
        output_folder_path = input("Please enter the path to the output folder: ")
        if os.path.isdir(output_folder_path):
            break
        else:
            create_folder = input("The output folder does not exist. Do you want to create a new folder with this name? (y/n): ").strip().lower()
            if create_folder == 'y':
                os.makedirs(output_folder_path, exist_ok=True)
                break
            elif create_folder == 'n':
                print("Please enter a valid output folder path.")
            else:
                print("Invalid input. Please respond with 'y' for yes or 'n' for no.")
    # pipeline
    function(input_file_path, output_folder_path)

