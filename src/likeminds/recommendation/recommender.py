"""Module for ranking users by post overlap."""

from collections.abc import Hashable
from typing import List

import pandas as pd


def rank_users_by_post_overlap(
    user_id: Hashable,
    liked_posts_df: pd.DataFrame,
) -> List[Hashable]:
    """
    Rank users by the number of overlapping liked posts with the given user.

    Args:
        user_id: The target user to compare against other users.
        liked_posts_df: DataFrame with columns 'user_id' and 'post_id'.

    Returns:
        Ranked list of user IDs sorted by most overlapping liked posts.

    Raises:
        ValueError: If the DataFrame lacks required columns.
    """
    # Validate input DataFrame columns
    if set(liked_posts_df.columns) != {"user_id", "post_id"}:
        msg = "DataFrame must contain 'user_id' and 'post_id' columns"
        raise ValueError(msg)

    # Ensure user_id exists in the dataframe
    if user_id not in liked_posts_df["user_id"].values:
        return []

    # Get the set of posts liked by the target user
    target_user_posts = set(
        liked_posts_df[liked_posts_df["user_id"] == user_id]["post_id"]
    )

    # Compute post overlaps for each user
    user_post_overlaps = {}
    for user, group in liked_posts_df.groupby("user_id"):
        if user != user_id:
            other_other_posts = set(group["post_id"])
            user_post_overlaps[user] = len(other_other_posts & target_user_posts) / len(
                other_other_posts
            )

    # Sort users by number of overlapping posts in descending order
    return sorted(
        user_post_overlaps.keys(),
        key=lambda x: user_post_overlaps[x],
        reverse=True,
    )
