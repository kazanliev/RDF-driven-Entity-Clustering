import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

def get_hypernym(entity):
    """
    Query DBpedia to extract the hypernym of a given entity.
    
    Args:
    - entity (str): entity name (part of the URI after the last '/').
    
    Returns:
    - str: The hypernym of the entity if found. Otherwise, 'Not found'.
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    formatted_entity = entity.replace(' ', '_')  
    dbpedia_uri = f"http://dbpedia.org/resource/{formatted_entity}"
    
    # query to extract the hypernym
    query = f"""
    SELECT ?hypernym WHERE {{
        <{dbpedia_uri}> <http://purl.org/linguistics/gold/hypernym> ?hypernym .
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            hypernym_uri = results["results"]["bindings"][0]["hypernym"]["value"]
            # return last part of the URI 
            return hypernym_uri.split('/')[-1]  
    except Exception as e:
        print(f"Error querying DBpedia for {entity}: {e}")
    return "Not found"


def enrich_entities_with_hypernyms(input_csv_path, output_csv_path):
    """
    Read a file containing entities, query DBpedia for hypernyms of entities, and save the results in a new CSV.
    
    Args:
    - input_csv_path (str): Path to the input CSV (or ttl) file containing the complete list of entities.
    - output_csv_path (str): Path to the output CSV file to save entities and their hypernyms.
    """
    df = pd.read_csv(input_csv_path)
    
    df['Hypernym'] = df['Entity'].apply(get_hypernym)
    
    # Save 
    df.to_csv(output_csv_path, index=False)
    print(f'[INFO] Created hypernym dictionary for {input_csv_path} and saved to {output_csv_path}')
