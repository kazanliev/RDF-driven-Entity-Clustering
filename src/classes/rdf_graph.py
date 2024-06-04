import re
import os

BLANK_NODE = '_:b0'

class RDFGraph:
    """
    A class to represent an RDF graph
    """

    def __init__(self):
        self.triples = set()

    def size(self):
        """
        Return the number of triples in the graph
        """
        return len(self.get_triples())

    def add_triple(self, subject, predicate, obj):
        """
        Add a triple to the graph
        """
        self.triples.add((subject, predicate, obj))

    def remove_triple(self, subject, predicate, obj):
        """
        Remove a triple from the graph
        """
        self.triples.discard((subject, predicate, obj))

    def add_multiple_triples(self, triples):
        """
        Add multiple triples to the graph.
        """
        self.triples.update(triples)

    def remove_multiple_triples(self, triples):
        """
        Remove multiple triples from the graph.
        """
        for triple in triples:
            self.triples.discard(triple)

    def add_from_turtle(self, file_path):
        """
        Parse triples from the specified turtle file and add them to the graph
        """
        if os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                for line in f:
                    match = re.match(r'<([^<>]*)> <([^<>]*)> (<([^<>]*)>|_:\w+) \.', line.strip())
                    if match:
                        subj, pred, blank, obj = match.groups()
                        if blank == BLANK_NODE:
                            self.add_triple(subj, pred, BLANK_NODE)
                        else:
                            self.add_triple(subj, pred, obj)
        else:
            print(f'[WARNING] No triples added from {file_path} (empty graph)')
                        

    def save_to_turtle(self, file_path):
        """
        Save an RDF graph to a turtle file
        """
        # Save in alphabetical order
        if (self.size()==0):
            print(f'[WARNING] Saving empty graph to {file_path}')
        sorted_triples = sorted(self.triples, key=lambda triple: triple[0])  
        with open(file_path, 'w') as f:
            for subj, pred, obj in sorted_triples:
                if obj == BLANK_NODE:
                    f.write(f'<{subj}> <{pred}> {obj} .\n')
                else:
                    f.write(f'<{subj}> <{pred}> <{obj}> .\n')


    def print_triples(self):
        for subj, pred, obj in self.triples:
            if obj == BLANK_NODE:
                print(f'<{subj}> <{pred}> {obj}')
            else:
                print(f'<{subj}> <{pred}> <{obj}>')

    def merge_graphs(self, other_graph):
        """
        Merges the current graph with another RDFGraph object
        """
        self.triples = self.triples.union(other_graph.triples)

    def get_triples(self):
        """
        Returns a set of all triples in the graph.
        """
        return self.triples

    def get_subjects(self):
        """
        Returns a set of all unique subjects in the graph.
        """
        return {subj for subj, _, _ in self.triples}
    
    def entity_predicate_dict(self, input_file):
        """
        Parse a graph from a turtle file and returns a dictionary 
        with a set of predicates for each graph subject 
        """
        entity_predicate_dict = {}
        self.add_from_turtle(input_file)
        for triple in self.get_triples():
            subject, predicate, _ = triple
            if subject not in entity_predicate_dict:
                entity_predicate_dict[subject] = set()
            entity_predicate_dict[subject].add(predicate)
        return entity_predicate_dict
    
    


