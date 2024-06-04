import pandas as pd
from src.classes.rdf_graph import RDFGraph

def process_exclude_forbidden_properties(input_file, excluded_prop_file, output_file):
    """
    Exclude triples which contains 'forbidden' properties (predicates), specified in the 'resources/forbidden.csv'.
    These are manually selected properties that are too common (or too uncommon) and do not contribute to describing
    the subject better. 

    Args:
        input_file (str): input file containing all properties for every entity
        excluded_prop_file (str): list of all 'forbidden' properties
        output_file (str): filtered csv list of properties for each entity
    """
    forbidden_list = pd.read_csv(excluded_prop_file)

    forbidden_list = forbidden_list.iloc[:, 0].tolist()
    g = RDFGraph()
    g.add_from_turtle(input_file)
    triple_set = g.get_triples()
    for triple in set(triple_set):
        subj, pred, obj = triple
        if pred in forbidden_list:
            g.remove_triple(subj, pred, obj)
    g.save_to_turtle(output_file)
    print(f"[INFO] Filtered entity properties from {input_file} using {excluded_prop_file}. Saved to {output_file}")
