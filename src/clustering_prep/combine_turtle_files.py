import os
from src.classes.rdf_graph import RDFGraph

def combine_turtle_files(file1_path, file2_path, output_file_path):
    """
    Combines REBEL triples and DBpedia triples in a single turtle file (for clustering).

    Args:
        file1_path (str): file containing triples extracted from the text (using NLP)
        file2_path (str): file containing DBpedia triples
        output_file_path (str):output file for the combined triples
    Raises:
        ValueError: If both of the files are empty, it means that no triples have been extracted from the input text.
    """

    # if both input files empty, break the pipeline (no triples have been extracted from the text)

    g = RDFGraph()
    g.add_from_turtle(file1_path)
    g.add_from_turtle(file2_path)
    # if both input files empty, break the pipeline (no triples have been extracted from the text)
    if g.size() == 0:
        raise ValueError(f"[ERROR]. No valid triples for clustering have been extracted from {file1_path} and {file2_path}. Breaking the pipeline.")
    g.save_to_turtle(output_file_path)

