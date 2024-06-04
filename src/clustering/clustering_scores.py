import numpy as np
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import fcluster


def cluster_data_sc_silhouette(Z, max_possible_clusters, similarity_matrix):
    """
    Determine the clustering with the highest Silhouette score 

    Args:
        Z (ndarray): hierarchical clustering matrix (matrix returned by the linkage function)
        max_possible_clusters (int): upper bound for the number of clusters (usually set to the number of entities)
        similarity_matrix (ndarray): similarity matrix

    Returns:
        final_clusters: selected clustering with the highest score
        best_num_clusters(int): number of clusters in the selected clustering
        best_score(float): value of the Silhouette score for the best rated clustering
    """
    best_num_clusters = 0
    best_score = -1     

    # If there are only 2 elements, cluster them
    # in two different clusters and return a default value of 0
    # In case of 2 elements, fcluster will usually return two clusters
    if len(similarity_matrix==2): 
        best_num_clusters = 2
        best_score = 0

    #distance matrix needed for computing Silhouette score
    distance_matrix = 1 - similarity_matrix
    for num_clusters in range(2, max_possible_clusters):
        # Silhouette score defined for 2 to number of samples - 1
        try:
            clusters = fcluster(Z, num_clusters, criterion="maxclust")
            # Note that Silhouette Coefficient is only defined if number if
            # 2 <= n_labels (number of different clusters) <= n_samples (number of entities) - 1
            # fcluster does not often produce only 1 cluster when num_clusters is very low
            # because this can be a better fit. 
            unique_clusters = np.unique(clusters)
            if len(unique_clusters) == 1:
                score = 0
                best_num_clusters = 1
            else:
                score = silhouette_score(distance_matrix, clusters, metric='precomputed')
                if score > best_score:
                    best_score = score
                    best_num_clusters = num_clusters

        except Exception as e:
            print(f"[INFO] Silhouette score calculation failed for {num_clusters} clusters: {str(e)}")

    # Return the best rated clustering
    final_clusters = fcluster(Z, best_num_clusters, criterion="maxclust")
    return final_clusters, best_num_clusters, best_score