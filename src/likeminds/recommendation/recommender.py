"""Module for ranking users by post overlap."""

from collections.abc import Hashable
from typing import List

import pandas as pd

def rank_users_by_post_overlap(
    profile_id: Hashable,
    liked_posts_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Rank users by the number of overlapping liked posts with the given user,
    and return a DataFrame with columns 'profile_id' and 'match_score' sorted in descending order.
    
    Args:
        profile_id: The target user to compare against other users.
        liked_posts_df: DataFrame with columns 'profile_id' and 'url'.
    
    Returns:
        DataFrame with columns:
            - 'profile_id': user identifier (string)
            - 'match_score': a score computed as the fraction of overlapping posts.
    
    Raises:
        ValueError: If the DataFrame lacks required columns.
    """
    # (Optional) Validate required columns exist in liked_posts_df
    required_cols = {"profile_id", "url"}
    if not required_cols.issubset(liked_posts_df.columns):
        msg = "DataFrame must contain 'profile_id' and 'url' columns"
        raise ValueError(msg)
    
    target_profile = profile_id
    # Convert the target profile to the expected format
    if ".bsky.social" not in profile_id:
        target_profile = f"{profile_id}.bsky.social"
        
    
    # Ensure the target profile exists in the DataFrame
    if target_profile not in liked_posts_df["profile_id"].values:
        print(f"Target profile {target_profile} not found in DataFrame.")
        return pd.DataFrame(columns=["profile_id", "match_score"])
    
    # Get the set of posts liked by the target user
    target_user_posts = set(
        liked_posts_df[liked_posts_df["profile_id"] == target_profile]["url"]
    )
    
    # Compute overlap score for each user (excluding the target)
    user_post_overlaps = {}
    for user, group in liked_posts_df.groupby("profile_id"):
        if user != target_profile:
            other_posts = set(group["url"])
            # Compute match score as the fraction of this user's posts that overlap with the target
            # (You can adjust this formula as needed)
            if len(other_posts) > 0:
                match_score = len(other_posts & target_user_posts) / len(other_posts)
            else:
                match_score = 0
            user_post_overlaps[user] = match_score

    # Create a DataFrame from the computed scores and sort in descending order
    results_df = pd.DataFrame(
        list(user_post_overlaps.items()),
        columns=["profile_id", "match_score"]
    )
    results_df = results_df.sort_values(by="match_score", ascending=False).reset_index(drop=True)
    
    return results_df


if __name__ == "__main__":
    df = pd.read_csv("data/user_likes.csv")
    print(rank_users_by_post_overlap(profile_id=10, liked_posts_df=df))
