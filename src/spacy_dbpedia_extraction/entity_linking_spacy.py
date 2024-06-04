import spacy
import requests
import csv
from src.classes.rdf_graph import RDFGraph

# Use spaCy’s pipeline for extracting named entities (https://spacy.io/usage/processing-pipelines)
nlp = spacy.load("en_core_web_sm")


def link_entities_to_dbpedia(entities, confidence = 0.9):
    """
    Links the entities to DBpedia URIs. Entities with no corresponding DBpedia URIs are discarded.

    Args:
        entities (list): list of entities
        confidence (float, optional): Higher confidence value corresponds to higher accuracy when linking.
        We use a value of 0.9

    Returns:
        dbpedia_resources (dict): linked entities and their corresponding DBpedia URIs
    """
    total_num_of_entities = len(entities)
    print(f"[INFO] {total_num_of_entities} entities have been found. Typically, not all of them will be linked to DBpedia URIs")


    dbpedia_resources = set()
    count=0
    for entity in entities:
        # Call DBpedia Spotlight API
        response = requests.get(f'https://api.dbpedia-spotlight.org/en/annotate?text={entity}&confidence={confidence}', headers={'accept': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            resources = data.get('Resources', [])
            if resources:
                # Take the first URI found (highest probability to be matching)
                dbpedia_resources.add((entity, resources[0]['@URI']))
                count+=1
                # Show output to the user to track progress
                if count % 50 == 0:
                    print(f"[INFO] {count}/{total_num_of_entities} already linked to a DBpedia URI")
    print(f"[INFO] A total of {count}/{total_num_of_entities} (spaCy) entities have been linked to a DBpedia URI")
    return dbpedia_resources

def save_to_csv(dbpedia_entities, file_path):
    """
    Helper function to save entities (extracted with spaCy) and their corresponding DBpedia URIs to a csv file.

    Args:
        dbpedia_entities (_type_): 
        file_path (str): csv file destination
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Entity', 'DBpedia_URI'])
        for entity, dbpedia_resource in dbpedia_entities:
            writer.writerow([entity, dbpedia_resource])

def process_entity_linking(input_file_path, output_file_path):
    """
    Processes entity (subjects) linking to DBpedia URIs for all the extracted named entities (using spaCy's pipeline)
    """
    with open(input_file_path, 'r') as text:
        # Use the spaCy pipeline for extracting entities
        # Source: https://spacy.io/usage/processing-pipelines
        doc = nlp(text.read())
        entities = {entity.text for entity in doc.ents}
        dbpedia_entities = link_entities_to_dbpedia(entities)
        save_to_csv(dbpedia_entities, output_file_path)
        print(f'Extracted entities from {input_file_path} with (spaCy) have been linked to DBpedia URIs saved to {output_file_path}')

