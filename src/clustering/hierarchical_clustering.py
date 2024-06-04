from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
from src.clustering.similarity_measures import one_hot_encode_entities, compute_jaccard_similarity, compute_sorensen_similarity, compute_cosine_similarity
from src.clustering.cluster_util import parse_rdf, save_dendrogram, save_clusters_to_json
from src.clustering.clustering_scores import cluster_data_sc_silhouette

def process_clustering_new(rdf_data, output_file, dendrogram_file_base, similarity_measure, clustering_method, clustering_score):
    """
    Process hierarchical clustering for given similarity measure, clustering (linkage) method and clustering score 

    Args:
        rdf_data (dict): parsed rdf data
        output_file (str): output file destination
        dendrogram_file_base (str): file base for the dendrogram destination folder
        similarity_measure (str): used similarity measure
        clustering_method (str): used clustering (linkage) method
        clustering_score (str): used clustering score 

    Returns:
        optimal_num_clusters(int): number of clusters of the best rated clustering
        best_score(float): the corresponding score
    """

    
    similarity_functions = {
        'jaccard': compute_jaccard_similarity,
        'sorensen': compute_sorensen_similarity,
        'cosine': compute_cosine_similarity
    }
    
    clustering_methods = {
        'average': 'average',
        'complete': 'complete',
        'single': 'single',
        'weighted': 'weighted',
        'centroid': 'centroid',
        'median': 'median',
        'ward': 'ward'
    }
    
    clustering_scores = {
        'Silhouette': cluster_data_sc_silhouette
    }

    # Compute similarity matrix
    compute_similarity = similarity_functions.get(similarity_measure)
    if not compute_similarity:
        raise ValueError(f"Invalid similarity measure: {similarity_measure}")
    similarity_matrix, subjects = compute_similarity(rdf_data)

    # We can also specify a lower value for max_possible_clusters if we want to set a lower bound.
    # But we cannot have more clusters than entities
    max_possible_clusters = len(subjects)

    # Perform hierarchical clustering
    clustering_method_func = clustering_methods.get(clustering_method)
    if not clustering_method_func:
        raise ValueError(f"Invalid clustering method: {clustering_method}")
    # Compute a distance matrix (in condensed form) for the linkage function
    distance_matrix = squareform(1-similarity_matrix)
    Z = linkage(distance_matrix, method=clustering_method_func)
    
    # Determine the best clustering using the linkage matrix Z
    coefficient_func = clustering_scores.get(clustering_score)
    if not coefficient_func:
        raise ValueError(f"Invalid clustering coefficient: {clustering_score}")
    clusters, optimal_num_clusters, best_score = coefficient_func(Z, max_possible_clusters, similarity_matrix)

    # Save dendrogram
    dendrogram_path = f"{dendrogram_file_base}_{similarity_measure}_{clustering_method}_{clustering_score}"
    save_dendrogram(Z, subjects, dendrogram_path, similarity_measure, clustering_method, clustering_score, optimal_num_clusters)
    
    # Save clustering
    new_output_file_json = f"{output_file}_{clustering_score}_{similarity_measure}_{clustering_method}.json"
    save_clusters_to_json(clusters, subjects, new_output_file_json)

    return optimal_num_clusters, best_score


def run_all_combinations(rdf_file_path, output_file_base, dendrogram_file_base):
    """
    For a given set of similarity measures, clustering methods and clustering scores, perform hierarchical clustering on rdf source
    and choose the best clustering for every combination of the three parameters. 

    Args:
        rdf_file_path (str): input file with extracted triples
        output_file_base (str): folder destination for the clusterings
        dendrogram_file_base (str): folder destination for the dendrograms

    Returns:
        results(dict): dict of computed best scores and corresponding number of clusters for the best-rated clustering (for every combination)
    """
    

    similarity_measures = ['jaccard', 'sorensen', 'cosine']
    clustering_methods = ['average', 'complete', 'single', 'weighted', 'centroid', 'median', 'ward']
    clustering_scores = ['Silhouette']

    # Parse data and compute similarity vectors outside of the functions for time efficiency
    rdf_data = parse_rdf(rdf_file_path)
    print("[INFO] Computing vectors for cosine similarity")
    if 'cosine' in similarity_measures:
        entity_vectors = one_hot_encode_entities(rdf_data)[0]
    print("[INFO] Vectors for cosine similarity computed")

    results = {}

    # For each combination return the number of clusters and score of the best rated clustering and save them
    for similarity_measure in similarity_measures:
        results[similarity_measure] = {}

        for clustering_method in clustering_methods:
            results[similarity_measure][clustering_method] = {}
            for clustering_score in clustering_scores:
                if similarity_measure == 'cosine':
                    num_clusters, score = process_clustering_new(entity_vectors, output_file_base, dendrogram_file_base, similarity_measure, clustering_method, clustering_score)
                else:
                    num_clusters, score = process_clustering_new(rdf_data, output_file_base, dendrogram_file_base, similarity_measure, clustering_method, clustering_score)
                
                results[similarity_measure][clustering_method][clustering_score] = {
                    'num_clusters': num_clusters,
                    'score': score
                }
                print(f"[INFO] Completed: {clustering_score}, {similarity_measure}, {clustering_method} ")

    # print
    for sim_measure, methods in results.items():
        for method, coeffs in methods.items():
            for coeff, result in coeffs.items():
                print(f"[INFO] Results for {sim_measure}, {method}, {coeff}: Clusters - {result['num_clusters']}, Score - {result['score']}")

    print(f"[INFO] Clustering results saved to {output_file_base}")
    print(f"[INFO] Dendrograms saved to {dendrogram_file_base}")
    return results
