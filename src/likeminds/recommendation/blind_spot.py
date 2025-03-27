import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances

def cluster_profiles_from_likes(likes_df: pd.DataFrame, n_clusters: int = 2) -> pd.DataFrame:
    """
    Given a DataFrame of likes (with at least 'profile_id' and 'uri' columns),
    generate a profile-post matrix and cluster the profiles into n_clusters.
    
    Args:
        likes_df (pd.DataFrame): DataFrame with columns 'profile_id' and 'uri'
        n_clusters (int): Number of clusters to form (default 2)
    
    Returns:
        pd.DataFrame: DataFrame mapping each profile_id to a cluster label.
    """
    # Create a binary matrix (profiles x posts)
    profile_post = pd.crosstab(likes_df['profile_id'], likes_df['uri'])
    
    # Use cosine distances for clustering (if the data is sparse and binary, this is often effective)
    distances = cosine_distances(profile_post)
    
    # Perform Agglomerative Clustering
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters, affinity='precomputed', linkage='average'
    )
    labels = clustering.fit_predict(distances)
    
    cluster_df = pd.DataFrame({"profile_id": profile_post.index, "cluster": labels})
    return cluster_df

def identify_blindspot_posts(likes_df: pd.DataFrame, cluster_df: pd.DataFrame, min_diff: int = 1) -> pd.DataFrame:
    """
    Identify posts that are 'blind spots'—liked much more by one cluster than another.
    
    Args:
        likes_df (pd.DataFrame): DataFrame with columns 'profile_id' and 'uri' (and optionally others).
        cluster_df (pd.DataFrame): DataFrame mapping profile_id to a cluster label.
        min_diff (int): Minimum difference between the max and min like counts across clusters 
                        for a post to be flagged (default 1).
    
    Returns:
        pd.DataFrame: DataFrame of posts (by uri) with like counts per cluster and the computed difference.
    """
    # Merge cluster labels with likes
    merged_df = likes_df.merge(cluster_df, on="profile_id", how="left")
    
    # Group by post (uri) and cluster, count likes
    group_counts = merged_df.groupby(["uri", "cluster"]).size().unstack(fill_value=0)
    
    # Compute the difference between the max and min counts across clusters for each post
    group_counts["diff"] = group_counts.max(axis=1) - group_counts.min(axis=1)
    
    # Filter posts where the difference is at least min_diff
    blindspots = group_counts[group_counts["diff"] >= min_diff].reset_index()
    
    return blindspots

# Example usage:
if __name__ == "__main__":
    # Suppose you have a DataFrame `likes_df` with the likes data:
    # Columns: ['profile_id', 'uri', 'liked_at', ...]
    # For example:
    data = {
        "profile_id": ["A", "A", "B", "B", "C", "C", "D", "D"],
        "uri": ["post1", "post2", "post1", "post2", "post1", "post3", "post1", "post3"]
    }
    likes_df = pd.DataFrame(data)
    
    # Cluster profiles into two groups based on their like patterns
    cluster_df = cluster_profiles_from_likes(likes_df, n_clusters=2)
    print("Cluster assignments:")
    print(cluster_df)
    
    # Identify blind spot posts (posts liked disproportionately by one group)
    blindspot_posts = identify_blindspot_posts(likes_df, cluster_df, min_diff=1)
    print("\nBlindspot posts:")
    print(blindspot_posts)