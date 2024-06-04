import os
import datetime
import src.rebel_extraction.text_to_chunks as text_to_chunks
import src.rebel_extraction.triples_extraction as triples_extraction
import src.spacy_dbpedia_extraction.entity_linking_spacy as entity_linking_spacy
import src.spacy_dbpedia_extraction.dbpedia_property_extraction as dbpedia_property_extraction
import src.clustering.hierarchical_clustering as hierarchical_clustering
import src.rebel_extraction.entity_linking_REBEL as entity_linking_REBEL
import src.spacy_dbpedia_extraction.exclude_forbidden_properties as exclude_forbidden_properties
import src.clustering_prep.combine_turtle_files as combine_turtle_files
import src.clustering_prep.combine_uris as combine_uris
import src.labeling.csv_dict_hypernym_enricher as csv_dict_hypernym_enricher
import src.labeling.cluster_hypernym_enricher as cluster_hypernym_enricher
import src.labeling.assign_label_to_clusters as assign_label_to_clusters
import src.evaluation_prep.labeling_dcterms_rdf_type as labeling_dcterms_rdf_type
import src.evaluation_prep.generate_statistics as generate_statistics
from src.util.util_main import OUTPUT_FOLDERS, get_timestamp, generate_paths, log_start_end, setup_logging, prompt_user_input

# Properties we want to exclude
EXCLUDED_PROPERTIES_FILE = 'resources/excluded_properties.csv'
# List of DBpedia hypernyms and their occurence counts
HYPERNYMS_COUNTS_FILE = 'resources/dbpedia_hypernym_counts.json'


# Main pipeline
def pipeline(input_file, output_folder):
    """
    Main pipeline function
    """

    # Check if the input file is empty
    if os.path.getsize(input_file) == 0:
        raise ValueError(f"[ERROR] The input file '{input_file}' is empty.")

    # Generate folder and file paths needed for the pipeline
    article_name = input_file.split('__')[-1].split('.')[0]
    base_name = os.path.splitext(os.path.basename(article_name))[0]
    for folder in OUTPUT_FOLDERS:
        os.makedirs(f'{output_folder}/{base_name}/{folder}', exist_ok=True)
    paths = generate_paths(output_folder, base_name)

    # Start
    logger = setup_logging(article_name)
    start_time = datetime.datetime.now()
    logger.info(f"Pipeline started at {get_timestamp()}")
    logger.info(f"INPUT TEXT: {article_name}")

    ## Section: REBEL triples extracting and linking
    # Partitioning of the input file to smaller chunks for REBEL to process
    text_to_chunks.chunk_text_file(input_file, paths["text_chunks"])
    logger.info("Text partitioning done")

    # REBEL triples extraction from the partitioning
    log_start_end(logger, "REBEL triples extraction", article_name,
                  lambda: triples_extraction.process_triples_extraction_REBEL(paths["text_chunks"], paths["REBEL_triples"], base_name))

    # Linking subjects of the REBEL triples to DBpedia URIs
    log_start_end(logger, "REBEL triples linking subjects to DBpedia URIs ", article_name,
                  lambda: entity_linking_REBEL.process_entity_linking(paths["REBEL_triples"], paths["REBEL_linked_triples"]))

    ## Section: SpaCy entity extraction and linking to DBpedia properties to generate triples
    # Extract entities from the input text with spaCy and link them to DBpedia URIs
    log_start_end(logger, "SpaCy entity extraction and mapping to DBpedia URIs", article_name,
                  lambda: entity_linking_spacy.process_entity_linking(input_file, paths["spacy_linked_entities"]))

    # For the spaCy entities (linked to DBpedia URIs) extract all properties from DBpedia
    # (also add dcterms:subject and rdf:type values to the list of properties for each entity)
    log_start_end(logger, "DBpedia property extraction for extracted entities", article_name,
                  lambda: dbpedia_property_extraction.process_property_extraction(paths["spacy_linked_entities"], 
                                                                               paths["spacy_entity_properties"], 
                                                                               paths["dcterms_rdf_prop_base"], 
                                                                               paths["REBEL_linked_triples"]))

    # Exclude triples with properties which do not contribute to better clustering
    exclude_forbidden_properties.process_exclude_forbidden_properties(paths["spacy_entity_properties"], EXCLUDED_PROPERTIES_FILE, paths["spacy_entity_properties"])
    logger.info("Removed triples containing forbidden properties")

    ## Section: Combining and filtering triples and entities to prepare for clustering
    # Combine REBEL triples and DBpedia entities (triples extracted from DBpedia for the spaCy entities)
    combine_turtle_files.combine_turtle_files(paths["REBEL_linked_triples"], paths["spacy_entity_properties"], paths["combined_triples"])
    logger.info("Combined REBEL Triples and DBpedia triples done")

    # Extract the URIs (after last '/') of all entities
    combine_uris.combine_uris(paths["REBEL_linked_triples"], paths["spacy_linked_entities"], paths["combined_entities"])
    logger.info("Saved URIs for all extracted entities")

    # Creating hypernym dictionary that maps each entity to its corresponding DBpedia hypenym
    log_start_end(logger, "Creating hypernym dictionary", article_name,
                  lambda: csv_dict_hypernym_enricher.enrich_entities_with_hypernyms(paths["combined_entities"], paths["hypernym_dict"]))

    ## Section: Clustering 
    # Process hierarchical clustering
    scores = log_start_end(logger, "Hierarchical clusterings", article_name,
                  lambda: hierarchical_clustering.run_all_combinations(paths["combined_triples"], paths["clustering_output_base"], paths["dendrograms_base"]))

    ## Section: Labeling
    # Add hypernyms to elements in each of the clusterings
    log_start_end(logger, "Adding hypernyms to clusters", article_name,
                  lambda: cluster_hypernym_enricher.hypernym_enricher_folder(paths["hypernym_dict"], paths["result_clusters"], paths["clusters_with_hypernyms"]))

    # Label clusters based on the extracted hypernyms
    assign_label_to_clusters.assign_label_to_clusters_folder(paths["clusters_with_hypernyms"], paths["labeled_clusters"], HYPERNYMS_COUNTS_FILE)
    logger.info("Label clusters based on hypernyms done")

    ## Section: Extracting further info to prepare for evaluation
    # Generate a summary conatining details of the clustering process
    generate_statistics.save_statistics(input_file, paths["REBEL_linked_triples"], paths["spacy_entity_properties"], paths["combined_triples"], paths["combined_entities"], scores, paths["statistics"])
    logger.info("Statistics extracted")

    # Add rdf:type and dcterms:subject values for every entity to the clusterings to facilitate evaluation
    labeling_dcterms_rdf_type.process_clusters_label_dcterms_rdf_folder(paths["labeled_clusters"], paths["labeled_clusters_dcterms_rdf"], paths["dcterms_rdf_prop_base"])
    logger.info("Adding rdf:type and dcterms:subject values done")

    # END
    end_time = datetime.datetime.now()
    logger.info(f"Pipeline ended at {get_timestamp()}")
    logger.info(f"Total execution time {(end_time - start_time).total_seconds()} seconds")

def main():
    prompt_user_input(pipeline)

if __name__ == '__main__':
    main()
