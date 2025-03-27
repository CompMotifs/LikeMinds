"""Module for ranking users by post overlap."""

from collections.abc import Hashable
from typing import List

import pandas as pd


def rank_users_by_post_overlap(
    profile_id: Hashable,
    liked_posts_df: pd.DataFrame,
) -> List[Hashable]:
    """
    Rank users by the number of overlapping liked posts with the given user.

    Args:
        profile_id: The target user to compare against other users.
        liked_posts_df: DataFrame with columns 'profile_id' and 'url'.

    Returns:
        Ranked list of user IDs sorted by most overlapping liked posts.

    Raises:
        ValueError: If the DataFrame lacks required columns.
    """
    # Validate input DataFrame columns
    # Todo add check
    # if len({"profile_id", "url"} - set(liked_posts_df.columns)) == 0:
    #     msg = "DataFrame must contain 'profile_id' and 'url' columns"
    #     raise ValueError(msg)

    # Ensure profile_id exists in the dataframe
    if profile_id not in liked_posts_df["profile_id"].values:
        return []

    # Get the set of posts liked by the target user
    target_user_posts = set(
        liked_posts_df[liked_posts_df["profile_id"] == profile_id]["url"]
    )

    # Compute post overlaps for each user
    user_post_overlaps = {}
    for user, group in liked_posts_df.groupby("profile_id"):
        if user != profile_id:
            other_other_posts = set(group["url"])
            user_post_overlaps[user] = len(other_other_posts & target_user_posts) / len(
                other_other_posts
            )

    # Sort users by number of overlapping posts in descending order
    return sorted(
        user_post_overlaps.keys(),
        key=lambda x: user_post_overlaps[x],
        reverse=True,
    )


if __name__ == "__main__":
    df = pd.read_csv("data/user_likes.csv")
    print(rank_users_by_post_overlap(user_id=10, liked_posts_df=df))
