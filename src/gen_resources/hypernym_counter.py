from SPARQLWrapper import SPARQLWrapper, JSON
import json

# NOTE: This function is not used in our pipeline. 

def fetch_and_save_hypernym_counts(output_file_path):
    """
    Extract the occurence counts for DBpedia hypernyms
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    
    query = """
    SELECT ?hypernym (COUNT(?resource) AS ?count) WHERE {
      ?resource <http://purl.org/linguistics/gold/hypernym> ?hypernym .
    } GROUP BY ?hypernym
    ORDER BY DESC(?count)
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    hypernyms = [{"hypernym": result["hypernym"]["value"].split('/')[-1], "count": int(result["count"]["value"])}
                 for result in results["results"]["bindings"]]
    
    with open(output_file_path, 'w') as json_file:
        json.dump(hypernyms, json_file, indent=4)

    print(f"Hypernyms saved to {output_file_path}")
