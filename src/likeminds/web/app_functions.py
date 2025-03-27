import sys
import os
# Add the parent directory to path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from likeminds.api.bluesky_api import (
    extract_post_likers,
    get_multiple_profiles_likes_df,
    get_unfollowed_users,
    extract_post_likers,
)
from likeminds.recommendation.recommender_word2vec import get_similar_users_dataframe


def seed_input_check(input_text: str) -> dict:
    """
    Checks if the input text is either a valid URL or a comma-separated list of handles.

    Returns a dictionary with:

      - valid (bool): True if the input is valid.
      - type (str): "url" if the input is a URL, or "handles" if it is a CSV list.
      - value: the URL (str) or list of handles.
      - error (str): error message if invalid.
    """

    input_text = input_text.strip()

    if not input_text:
        return {"valid": False, "error": "Seed input cannot be empty."}

    # Check if the input is a valid URL.

    from urllib.parse import urlparse

    parsed = urlparse(input_text)

    if parsed.scheme in ("http", "https") and parsed.netloc:
        return {"valid": True, "type": "url", "value": input_text}

    # Otherwise, assume it's a comma-separated list of handles.

    handles = [handle.strip() for handle in input_text.split(",") if handle.strip()]

    if handles:
        return {"valid": True, "type": "handles", "value": handles}

    return {
        "valid": False,
        "error": "Input must be a valid URL or a comma-separated list of handles.",
    }


def get_seed_accounts(url):
    """
    Return handles of users who liked the linked post.
    """
    liker_dict = extract_post_likers(post_url=url, max_likers=1000, rate_limit_delay=1)
    liker_handles = []
    for user in liker_dict:
        if "handle" in user and user["handle"]:
            liker_handles.append(user["handle"])
    return liker_handles


def likes_from_handles(list_of_handles):
    multiple_likes = get_multiple_profiles_likes_df(
        profile_ids=list_of_handles, total_posts_per_profile=1000, include_text=True
    )
    return multiple_likes[["profile_id", "url", "text"]]


# Example routine to generate matching users
"""
seed_accounts = get_seed_accounts('https://bsky.app/profile/coreyspowell.bsky.social/post/3llerbvse722r')
reference_user = seed_accounts[0]
likes_df = likes_from_handles(seed_accounts)


# Find users similar to the reference user
similar_users_df = get_similar_users_dataframe(
    likes_df,                              # Your dataframe with 'profile_id' and 'text' columns
    reference_user=reference_user,  # The user you want to find matches for
    top_n=5                          # Number of similar users to return
)

# Display the results
print(similar_users_df)'
"""

# Example 5: Find users that reference user doesn't follow
"""
# Get users who liked a post
post_url = "https://bsky.app/profile/cianodonnell.bsky.social/post/3ll7v4czwzc25"
likers = extract_post_likers(post_url, max_likers=50)

# # Filter to only users not followed by the reference account
reference_user = "compmotifs.bsky.social"
unfollowed_users = get_unfollowed_users(reference_user, likers)

print(f"Found {len(unfollowed_users)} users who liked the post but aren't followed by {reference_user}")
for user in unfollowed_users:  # Show first 5
    print(f"User: {user['handle']} ({user.get('displayName', 'No display name')})")
"""
