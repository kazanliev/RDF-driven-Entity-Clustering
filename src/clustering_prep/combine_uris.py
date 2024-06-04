import pandas as pd
from src.classes.rdf_graph import RDFGraph

def combine_uris(input_file_1, input_file_2, output_file):
    """
    Combines the URIs (last part after '/') of REBEL triples entities (subjects) and the URIs of those found by NER (spaCy).

    Args:
        input_file_1 (str): input file containing REBEL triples
        input_file_2 (str): list of found entities (using spaCy's pipeline) and their corresponding DBpedia URIs
        output_file (str): output file to save the combined entities (only the part after the last '/' is saved)
    """
    
    # Extract the descriptive part of the URI (the name of the entity)
    def extract_entity(uri):
        return uri.split('/')[-1]

    g = RDFGraph()
    g.add_from_turtle(input_file_1)
    uris_from_file1 = g.get_subjects()
    # Extract URIs of the entities found by NER (spaCy)
    csv_file2 = pd.read_csv(input_file_2)
    uris_from_file2 = csv_file2['DBpedia_URI'].unique()

    # Extract entity names and save unique list
    entities_from_file1 = [extract_entity(uri) for uri in uris_from_file1]
    entities_from_file2 = [extract_entity(uri) for uri in uris_from_file2]
    all_unique_entities = pd.unique(pd.concat([pd.Series(entities_from_file1), pd.Series(entities_from_file2)]))
    unique_entities = pd.DataFrame(all_unique_entities, columns=['Entity'])
    unique_entities.to_csv(output_file, index=False)


