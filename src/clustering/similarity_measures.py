import numpy as np
from scipy.spatial.distance import cosine

def one_hot_encode_entities(rdf_data):
    """
    Perform one-hot-encoding to compute property (predicate) vectors (input for cosine similarity).

    Args:
        rdf_data (dict): all entities and their corresponding properties after parsing

    Returns:
        entity_vectors(dict): property vectors for each entity
        unique_properties(list): ordered list of properties for reference
    """
    unique_properties = set()
    for entity, properties in rdf_data.items():
        unique_properties.update(properties)

    unique_properties = list(unique_properties)
    entity_vectors = {}
    for entity, properties in rdf_data.items():
        vector = np.zeros(len(unique_properties))
        for property in properties:
            if property in unique_properties:
                index = unique_properties.index(property)
                vector[index] = 1
        entity_vectors[entity] = vector

    return entity_vectors, unique_properties

def compute_jaccard_similarity(data):
    """
    Compute Jaccard similarity for each pair of CDs (candidate descriptions).

    Args:
        data(dict): all entities and their corresponding properties after parsing
    Returns:
        similarity_matrix(ndarray): similarity matrix
        subjects(list): ordered of entities (subjects)
    """
    subjects = list(data.keys())
    n = len(subjects)
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        similarity_matrix[i, i] = 1
        for j in range(i + 1, n):
            intersection = len(data[subjects[i]].intersection(data[subjects[j]]))
            union = len(data[subjects[i]].union(data[subjects[j]]))
            similarity = intersection / union if union != 0 else 0
            similarity_matrix[i, j] = similarity_matrix[j, i] = similarity

    return similarity_matrix, subjects

def compute_sorensen_similarity(data):
    """
    Compute Sorensen (Dice) similarity for each pair of CDs (candidate descriptions).

    Args:
        data(dict): all entities and their corresponding properties after parsing
    Returns:
        similarity_matrix(ndarray): similarity matrix
        subjects(list): ordered list of entities (subjects)
    """
    subjects = list(data.keys())
    n = len(subjects)
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        similarity_matrix[i, i] = 1  
        for j in range(i + 1, n):
            intersection = len(data[subjects[i]].intersection(data[subjects[j]]))
            sum = len(data[subjects[i]]) + len(data[subjects[j]]) 
            similarity = (2 * intersection) / sum if sum != 0 else 0
            similarity_matrix[i, j] = similarity_matrix[j, i] = similarity

    return similarity_matrix, subjects


def compute_cosine_similarity(entity_vectors):
    """
    Compute Cosine similarity for each pair of CDs (candidate descriptions).
    
    Args:
        entity_vectors(dict): all entity vectors computed via one-hot-encoding
    Returns:
        similarity_matrix(ndarray): similarity matrix
        subjects(list): ordered list of entities (subjects)
    """
    entities = list(entity_vectors.keys())
    n = len(entities)
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i, n):
            vec_i = entity_vectors[entities[i]]
            vec_j = entity_vectors[entities[j]]
            if i == j:
                similarity = 1  
            else:
                similarity = 1 - cosine(vec_i, vec_j)
            similarity_matrix[i, j] = similarity_matrix[j, i] = similarity

    return similarity_matrix, entities

