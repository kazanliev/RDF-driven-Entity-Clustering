import requests
import re
from src.classes.rdf_graph import RDFGraph
    
def link_entities_to_dbpedia(entities, confidence=0.9):
    """
    Links the entities to DBpedia URIs. Entities with no corresponding DBpedia URIs are discarded.

    Args:
        entities (list): list of entities
        confidence (float, optional): Higher confidence value corresponds to higher accuracy when linking.
        We use a value of 0.9

    Returns:
        dbpedia_entities (dict): linked entities and their corresponding DBpedia URIs
    """
    dbpedia_entities = {}
    count = 0
    total_num_of_entities = len(entities)
    for entity in entities:
        # Call DBpedia Spotlight API
        response = requests.get(f'https://api.dbpedia-spotlight.org/en/annotate?text={entity}&confidence={confidence}', headers={'accept': 'application/json'})
        if response.status_code == 200:
            # Note that if there is no URI found for the given entity at the specified confidence value,
            # the entity will be discarded from the set of entities.
            data = response.json()
            resources = data.get('Resources', [])
            if resources:
                # Take the first URI found (highest probability to be matching)
                dbpedia_entities[entity] = resources[0]['@URI'] 
                count += 1
                #Show output for the user to track progress
                if count % 50 == 0:
                    print(f"[INFO] {count}/{total_num_of_entities} (already) linked to a DBpedia URI")
    
    print(f"[INFO] A total of {count}/{total_num_of_entities} (REBEL) triple subjects have been linked to a DBpedia URI")
    return dbpedia_entities


def update_ttl_with_dbpedia_uris(input_file_path, dbpedia_entities, output_file_path):
    """
    Replace the subjects in the specified turtle input file with their corresponding DBpedia URIs.

    Args:
        input_file_path (str): input ttl file
        dbpedia_entities (dict): linked entities and their corresponding DBpedia URIs
        output_file_path (str): output file
    """
    with open(input_file_path, 'r', encoding='utf-8') as infile, \
         open(output_file_path, 'w', encoding='utf-8') as outfile:

         for line in infile:
            match = re.match(r'<(.*?)> <(.*?)> <(.*?)> \.', line.strip())
            if match:
                subject, predicate, obj = match.groups()
                
                # Check if the subject entity is in the dbpedia_entities set.
                # If not (no URI has been found), the triple will be discarded.
                if subject in dbpedia_entities:
                    subject = '<' + dbpedia_entities[subject] + '>'
                else: 
                    continue

                outfile.write(f"{subject} <{predicate}> <{obj}> .\n")

def process_entity_linking(input_file_path, output_file_path):
    """
    Processes entity (subjects) linking for DBpedia triples
    """
    g = RDFGraph()
    g.add_from_turtle(input_file_path)
    entities = g.get_subjects()
    dbpedia_entities = link_entities_to_dbpedia(entities)
    update_ttl_with_dbpedia_uris(input_file_path, dbpedia_entities, output_file_path)
    print(f'[INFO] REBEL Triple entities have been linked to DBpedia URIs saved to {output_file_path}')


