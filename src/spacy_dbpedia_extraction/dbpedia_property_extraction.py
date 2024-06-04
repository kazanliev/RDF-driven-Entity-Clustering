import csv
from SPARQLWrapper import SPARQLWrapper, JSON
from src.classes.rdf_graph import RDFGraph, BLANK_NODE

def get_properties(entity_uri):
    """
    Fetches all properties found for the given URI in DBpedia and also the values of the rdf:type and dcterms:subject properties
    (rdf:type and dcterms:subject values are handled as properties (predicates))

    Args:
        entity_uri (str): DBpedia URI

    Return:
        type_values (list): list of all values of the rdf:type property
        subject_values (list): list of all values of the dcterms:subject property
        property_values (list): list of all found properties for the specified URI

    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    # Ensure the URI is formatted correctly
    if not entity_uri.startswith("<"):
        entity_uri = f"<{entity_uri}>"
    if not entity_uri.endswith(">"):
        entity_uri = f"{entity_uri}>"

    # Query to fetch all properties
    query = """
    SELECT DISTINCT ?property WHERE {
      %s ?property ?o
    }
    """ % entity_uri
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results_properties = sparql.query().convert()

    # Query to fetch rdf:type values
    query_type = f"""
    SELECT DISTINCT ?type WHERE {{
      {entity_uri} rdf:type ?type.
    }}
    """
    sparql.setQuery(query_type)
    sparql.setReturnFormat(JSON)
    results_type = sparql.query().convert()

    # Query to fetch dcterms:subject values
    query_subject = f"""
    SELECT DISTINCT ?subject WHERE {{
      {entity_uri} dcterms:subject ?subject.
    }}
    """
    sparql.setQuery(query_subject)
    results_subject = sparql.query().convert()

    type_values = [result['type']['value'] for result in results_type["results"]["bindings"]]
    subject_values = [result['subject']['value'] for result in results_subject["results"]["bindings"]]
    property_values = [result['property']['value'] for result in results_properties["results"]["bindings"]]

    return property_values, type_values, subject_values

def process_property_extraction(input_file, output_file, dcterms_rdf_file_base, entity_linking_REBEL_output_file):
    """
    Processes extraction of properties (and values of dcterms:subject and rdf:type, handled as properties (predicates) for all URIs.

    Args:
        input_file (str): input csv file containing entities and corresponding URIs
        output_file (str): output csv file 
    """
    entities = set()
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        count = 0
        next(reader) 
        for row in reader:
            count += 1
            #DBpedia URIs are in the second column
            entities.add(row[1])  
        # Note that this is actually counting the list of URIs with repetitions, which
        # is equal to the list of different spaCy entities 
        # (some may have been mapped to equal URIs)
        num_of_entities_before_linking = count

    # Get the list of entities (subjects) from REBEL triples
    g_rebel_entities = RDFGraph()
    g_rebel_entities.add_from_turtle(entity_linking_REBEL_output_file)
    rebel_entities = g_rebel_entities.get_subjects()

    # Save the REBEL triples that are not part of the spaCy entities after linking
    linked_rebel_entities_added = rebel_entities.difference(entities)
    num_linked_rebel_entities_added = len(linked_rebel_entities_added)

    # Update the list of entities to also include REBEL subjects for DBpedia property extraction
    if num_linked_rebel_entities_added > 0:
        entities.update(linked_rebel_entities_added)
        print(f"[INFO] {num_linked_rebel_entities_added} URIs added from REBEL that were not part of the spaCy entities!")
        # for entity in linked_rebel_entities_added:
        #     print(entity)

    num_of_uris = len(entities)
    # Because two spaCy entities can map to the same URI 
    # (e.g., "Charles VI's" and "Charles VI" map to http://dbpedia.org/resource/Charles_VI_of_France),
    # we check how many unique entities remain.
    total_num_of_entities = num_of_entities_before_linking+num_linked_rebel_entities_added
    if num_of_entities_before_linking > num_of_uris:
        print(f"[INFO] {total_num_of_entities} entities reduced to {num_of_uris} after matching to DBpedia URIs")

    g = RDFGraph()
    # We also save separate graphs containing subjects only with 
    # rdf:type, repspectively dcterms:subject values as properties 
    # for later use in the evaluation
    g_rdf_type = RDFGraph()
    g_dcterms_subject = RDFGraph()
    count = 0
    for entity in entities:
        count+=1
        property_values, rdf_type_values, dcterms_subject_values = get_properties(entity)
        for value in rdf_type_values:
            g.add_triple(entity, value, BLANK_NODE)
            g_rdf_type.add_triple(entity,value, BLANK_NODE)
        for value in dcterms_subject_values:
            g.add_triple(entity, value, BLANK_NODE)
            g_dcterms_subject.add_triple(entity,value, BLANK_NODE)
        for value in property_values:
            g.add_triple(entity, value, BLANK_NODE)
        if count % 50 == 0:
            print(f"[INFO] {count}/{num_of_uris} entity-property sets have been extracted") 

    # Save the output graph 
    g.save_to_turtle(output_file)   
    rdf_type_output_file = f'{dcterms_rdf_file_base}_rdf_type.ttl'
    dcterms_subject_output_file = f'{dcterms_rdf_file_base}_dcterms_subject.ttl'
    # Save the rdf:type extracted properties separately for later use
    g_rdf_type.save_to_turtle(rdf_type_output_file)
    # Save the dcterms:subject extracted properties separately for later use
    g_dcterms_subject.save_to_turtle(dcterms_subject_output_file)               
    print(f"[INFO] A total of {count}/{num_of_uris} entity-property sets have been extracted")
    print(f"[INFO] Extracted DBpedia predicates for {input_file} and save to {output_file}.")
