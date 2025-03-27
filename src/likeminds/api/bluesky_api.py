"""
Bluesky Social Network API Utilities

This module provides functions for interacting with the Bluesky social network API,
specifically for extracting information about user likes and post interactions.

Functions:
- Basic API utilities to resolve DIDs and service endpoints
- Extract likes from user profiles
- Retrieve information about post likers
- Process data from multiple profiles in parallel

Requirements:
- requests
- pandas
- concurrent.futures (standard library)
"""

import requests
import json
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Union, Optional, Any


# --- Basic API Utilities ---

def get_did_from_handle(handle: str) -> str:
    """
    Convert a Bluesky handle to a Decentralized Identifier (DID).
    
    Args:
        handle: Bluesky handle (e.g., 'username.bsky.social')
        
    Returns:
        str: The user's DID
        
    Raises:
        Exception: If the handle cannot be resolved
    """
    response = requests.get(
        "https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle",
        params={"handle": handle}
    )
    if not response.ok:
        raise Exception(f"Failed to resolve handle: {response.status_code}")
    return response.json()["did"]


def get_service_endpoint(did: str) -> str:
    """
    Get the Personal Data Server (PDS) service endpoint for a DID.
    
    Args:
        did: Decentralized Identifier
        
    Returns:
        str: The service endpoint URL
        
    Raises:
        Exception: If the DID info cannot be retrieved or service endpoint not found
    """
    if did.startswith('did:web:'):
        response = requests.get(f"https://{did[8:]}/.well-known/did.json")
    else:
        response = requests.get(f"https://plc.directory/{did}")
    
    if not response.ok:
        raise Exception(f"Failed to get DID info: {response.status_code}")
    
    did_info = response.json()
    if not did_info.get("service") or not did_info["service"][0]:
        raise Exception("Could not find service endpoint")
    
    return did_info["service"][0]["serviceEndpoint"]


def extract_post_info(uri: str) -> Dict[str, str]:
    """
    Extract basic information about a post from its URI.
    
    Args:
        uri: AT protocol URI for a post
        
    Returns:
        dict: Post information including repo, collection, rkey, and web URL
    """
    parts = uri.split("/")
    return {
        "repo": parts[2],
        "collection": parts[3],
        "rkey": parts[4],
        "url": f"https://bsky.app/profile/{parts[2]}/post/{parts[4]}"
    }


# --- Post Details API ---

def get_post_details(post_uris: List[str]) -> List[Dict[str, Any]]:
    """
    Get detailed information about posts from their URIs.
    
    Args:
        post_uris: List of post URIs to retrieve
        
    Returns:
        list: Post details for each URI
        
    Raises:
        Exception: If the posts cannot be retrieved
    """
    if not post_uris:
        return []
    
    # API has a limit on the number of URIs per request
    # Split into chunks of 25 if needed
    max_uris_per_request = 25
    all_posts = []
    
    for i in range(0, len(post_uris), max_uris_per_request):
        chunk = post_uris[i:i + max_uris_per_request]
        response = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts",
            params={"uris": chunk}
        )
        if not response.ok:
            raise Exception(f"Failed to get posts: {response.status_code}")
        
        all_posts.extend(response.json().get("posts", []))
    
    return all_posts


# --- Profile Likes Extraction ---

def get_likes_df(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Get likes from a Bluesky profile and return as a pandas DataFrame.
    
    Args:
        config: Configuration dictionary with the following keys:
            - profile_id: Bluesky handle or DID (required)
            - total_posts: Total number of posts to extract (default 25)
            - include_text: Whether to include post text (default True)
            - rate_limit_delay: Time to wait between requests in seconds (default 1)
        
    Returns:
        DataFrame: Pandas DataFrame with liked posts and their details
        
    Raises:
        ValueError: If profile_id is missing
        Exception: If API requests fail
    """
    # Extract config parameters with defaults
    profile_id = config.get("profile_id")
    total_posts = config.get("total_posts", 25)
    include_text = config.get("include_text", True)
    rate_limit_delay = config.get("rate_limit_delay", 1)
    
    if not profile_id:
        raise ValueError("profile_id is required")
    
    # Convert handle to DID if needed
    did = profile_id if profile_id.startswith('did:') else get_did_from_handle(profile_id)
    
    # Get the PDS endpoint
    endpoint = get_service_endpoint(did)
    
    all_likes = []
    cursor = None
    limit_per_page = min(100, total_posts)  # Max 100 per API limitation
    
    # Paginate through likes until we have enough or there are no more
    while len(all_likes) < total_posts:
        # Set up request parameters
        params = {
            "repo": did,
            "collection": "app.bsky.feed.like",
            "limit": min(limit_per_page, total_posts - len(all_likes))
        }
        if cursor:
            params["cursor"] = cursor
        
        # Make the request
        response = requests.get(
            f"{endpoint}/xrpc/com.atproto.repo.listRecords",
            params=params
        )
        if not response.ok:
            raise Exception(f"Failed to get likes: {response.status_code}")
        
        likes_data = response.json()
        
        # Extract post URIs from likes
        post_uris = []
        new_likes = []
        
        for like_record in likes_data.get("records", []):
            subject = like_record.get("value", {}).get("subject", {})
            uri = subject.get("uri", "")
            # Only include app.bsky.feed.post URIs
            if "/app.bsky.feed.post/" in uri:
                post_uris.append(uri)
                post_info = extract_post_info(uri)
                new_likes.append({
                    "uri": uri,
                    "liked_at": like_record.get("value", {}).get("createdAt"),
                    "url": post_info["url"],
                    "author": post_info["repo"]
                })
        
        # Get post details if requested
        if include_text and post_uris:
            posts_details = get_post_details(post_uris)
            
            # Add post text to like records
            for like in new_likes:
                post_detail = next((p for p in posts_details if p["uri"] == like["uri"]), None)
                if post_detail:
                    if "record" in post_detail and "text" in post_detail["record"]:
                        like["text"] = post_detail["record"]["text"]
                    if "author" in post_detail:
                        like["author_handle"] = post_detail["author"].get("handle", "")
                        like["author_display_name"] = post_detail["author"].get("displayName", "")
                    like["repost_count"] = post_detail.get("repostCount", 0)
                    like["like_count"] = post_detail.get("likeCount", 0)
                    like["reply_count"] = post_detail.get("replyCount", 0)
                else:
                    like["text"] = ""
        
        all_likes.extend(new_likes)
        
        # Check if there are more records
        cursor = likes_data.get("cursor")
        if not cursor:
            break
        
        # Respect rate limits
        time.sleep(rate_limit_delay)
    
    # Trim to the exact number requested
    all_likes = all_likes[:total_posts]
    
    # Convert to DataFrame
    df = pd.DataFrame(all_likes)
    
    return df


def get_multiple_profiles_likes_df(
    profile_ids: List[Union[str, Dict[str, str]]], 
    total_posts_per_profile: int, 
    include_text: bool = False, 
    max_workers: int = 5
) -> pd.DataFrame:
    """
    Get likes from multiple Bluesky profiles and return as a combined pandas DataFrame.
    
    Args:
        profile_ids: List of Bluesky handles, DIDs, or dicts with 'did' and 'handle' keys
        total_posts_per_profile: Number of posts to extract per profile
        include_text: Whether to include post text (default False)
        max_workers: Maximum number of concurrent requests (default 5)
        
    Returns:
        DataFrame: Pandas DataFrame with liked posts and their details
    """
    # Function to process a single profile
    def process_profile(profile_entry):
        # Handle different input formats
        if isinstance(profile_entry, dict):
            profile_id = profile_entry.get('did')
            profile_handle = profile_entry.get('handle')
        else:
            profile_id = profile_entry
            profile_handle = None
            
        config = {
            "profile_id": profile_id,
            "total_posts": total_posts_per_profile,
            "include_text": include_text,
            "rate_limit_delay": 1
        }
        
        try:
            df = get_likes_df(config)
            # Add profile info columns
            df["profile_id"] = profile_id
            if profile_handle:
                df["profile_handle"] = profile_handle
            return df
        except Exception as e:
            print(f"Error processing {profile_id}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    # Process profiles concurrently with rate limiting
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_profile, profile_ids))
    
    # Combine all results
    combined_df = pd.concat(results, ignore_index=True)
    
    # Select only the needed columns
    base_columns = ["profile_id", "uri", "url", "author", "author_handle", "liked_at"]
    if "profile_handle" in combined_df.columns:
        base_columns.insert(1, "profile_handle")
    if include_text and "text" in combined_df.columns:
        base_columns.append("text")
    
    # Filter to only include columns that exist
    existing_columns = [col for col in base_columns if col in combined_df.columns]
    
    return combined_df[existing_columns]


# --- Post Likers Extraction ---

def extract_post_likers(post_url: str, max_likers: int = 100, rate_limit_delay: float = 1) -> List[Dict[str, str]]:
    """
    Extract profiles that liked a specific post.
    
    Args:
        post_url: URL or URI of the post
        max_likers: Maximum number of likers to extract
        rate_limit_delay: Time to wait between requests in seconds
        
    Returns:
        list: List of dictionaries with liker information (did, handle, displayName)
        
    Raises:
        ValueError: If the URL format is invalid
        Exception: If API requests fail
    """
    # Parse the post URL to get URI components
    if post_url.startswith("https://bsky.app/profile/"):
        # Format: https://bsky.app/profile/{handle}/post/{rkey}
        parts = post_url.split("/")
        if len(parts) < 6:
            raise ValueError("Invalid post URL format")
        
        handle = parts[4]
        rkey = parts[6]
        
        # Resolve handle to DID
        did = get_did_from_handle(handle)
        
        # Construct URI
        uri = f"at://{did}/app.bsky.feed.post/{rkey}"
    elif post_url.startswith("at://"):
        # Already in AT URI format
        uri = post_url
    else:
        raise ValueError("Unsupported URL format. Use https://bsky.app/profile/... or at://...")
    
    # Get the post's record
    post_response = requests.get(
        "https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread",
        params={"uri": uri, "depth": 0}
    )
    
    if not post_response.ok:
        raise Exception(f"Failed to get post: {post_response.status_code}")
    
    # Extract information from post
    post_data = post_response.json()
    if "thread" not in post_data or "post" not in post_data["thread"]:
        raise Exception("Invalid post data returned")
    
    post = post_data["thread"]["post"]
    post_cid = post.get("cid")
    
    if not post_cid:
        raise Exception("Could not find post CID")
    
    # Get likes for the post
    cursor = None
    likers = []
    
    while len(likers) < max_likers:
        params = {
            "uri": uri,
            "cid": post_cid,
            "limit": min(100, max_likers - len(likers))
        }
        
        if cursor:
            params["cursor"] = cursor
        
        likes_response = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getLikes",
            params=params
        )
        
        if not likes_response.ok:
            raise Exception(f"Failed to get likes: {likes_response.status_code}")
        
        likes_data = likes_response.json()
        
        # Extract liker profiles
        for like in likes_data.get("likes", []):
            if "actor" in like:
                actor = like["actor"]
                likers.append({
                    "did": actor.get("did", ""),
                    "handle": actor.get("handle", ""),
                    "displayName": actor.get("displayName", "")
                })
        
        # Check if there are more likes
        cursor = likes_data.get("cursor")
        if not cursor or len(likes_data.get("likes", [])) == 0:
            break
        
        # Respect rate limits
        time.sleep(rate_limit_delay)
    
    return likers[:max_likers]


def get_unfollowed_users(reference_user: str, user_list: List[Union[str, Dict[str, str]]]) -> List[Union[str, Dict[str, str]]]:
    """
    Filter a list of users to include only those not followed by the reference user.
    
    Args:
        reference_user: The handle or DID of the reference user
        user_list: List of user handles, DIDs, or dictionaries with 'did' and 'handle' keys
        
    Returns:
        list: Filtered list of users not followed by the reference user, in the same format as input
        
    Raises:
        Exception: If API requests fail
    """
    # First, standardize the user_list to include DIDs
    standardized_users = []
    for user in user_list:
        if isinstance(user, dict):
            if "did" in user:
                standardized_users.append(user)
            elif "handle" in user:
                # Convert handle to DID and create new dict
                did = get_did_from_handle(user["handle"])
                standardized_users.append({"did": did, "handle": user["handle"]})
        else:
            # String input - could be handle or DID
            if user.startswith("did:"):
                standardized_users.append({"did": user})
            else:
                # Convert handle to DID
                did = get_did_from_handle(user)
                standardized_users.append({"did": did, "handle": user})
    
    # Get the reference user's DID if it's a handle
    ref_did = reference_user if reference_user.startswith("did:") else get_did_from_handle(reference_user)
    
    # Initialize cursor and followed accounts list
    cursor = None
    followed_dids = set()
    
    # Get the list of accounts the reference user follows
    while True:
        params = {
            "actor": ref_did,
            "limit": 100
        }
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows",
            params=params
        )
        
        if not response.ok:
            raise Exception(f"Failed to get follows: {response.status_code}")
        
        follows_data = response.json()
        
        # Extract DIDs of followed accounts
        for follow in follows_data.get("follows", []):
            followed_dids.add(follow.get("did"))
        
        # Check if there are more follows
        cursor = follows_data.get("cursor")
        if not cursor:
            break
    
    # Filter out users that are already followed
    unfollowed_users = []
    for user in standardized_users:
        if user["did"] not in followed_dids:
            # Return in same format as input
            if isinstance(user_list[0], dict):
                unfollowed_users.append(user)
            else:
                # If input was strings, return the handle if available, otherwise the DID
                unfollowed_users.append(user.get("handle", user["did"]))
    
    return unfollowed_users

# --- Example Use Cases ---

"""
Example Use Cases

These examples demonstrate how to use the functions in this module
for common scenarios in Bluesky network analysis.
"""

# Example 1: Extract likes from a single profile
# ----------------------------------------------
# config = {
#     "profile_id": "bsky.app",  # Target handle
#     "total_posts": 50,         # Number of likes to extract
#     "include_text": True       # Include post content
# }
# 
# # Get the likes as a DataFrame
# profile_likes = get_likes_df(config)
# 
# # Display basic information
# print(f"Extracted {len(profile_likes)} likes from bsky.app")
# print(profile_likes[["url", "liked_at", "text"]].head())


# Example 2: Find users who liked a specific post
# ----------------------------------------------
# post_url = "https://bsky.app/profile/bsky.app/post/3kl5q7qhny22l"
# 
# # Get up to 50 users who liked this post
# post_likers = extract_post_likers(post_url, max_likers=50)
# 
# # Display information about these users
# print(f"Found {len(post_likers)} users who liked the post")
# for liker in post_likers[:5]:  # Show first 5
#     print(f"User: {liker['handle']} ({liker['displayName']})")


# Example 3: Analyze likes from multiple profiles
# ----------------------------------------------
# # Define list of profiles to analyze
# profiles = [
#     "user1.bsky.social",
#     "user2.bsky.social",
#     "user3.bsky.social"
# ]
# 
# # Extract 20 most recent likes from each profile
# multiple_likes = get_multiple_profiles_likes_df(
#     profile_ids=profiles,
#     total_posts_per_profile=20,
#     include_text=True
# )
# 
# # Display combined results
# print(f"Extracted {len(multiple_likes)} total likes from {len(profiles)} profiles")
# print(multiple_likes[["profile_id", "url", "liked_at"]].head())


# Example 4: Community analysis by combining examples
# ----------------------------------------------
# # First, find users who liked a specific post
# target_post = "https://bsky.app/profile/bsky.app/post/3kl5q7qhny22l"
# likers = extract_post_likers(target_post, max_likers=25)
# print(f"Found {len(likers)} users who liked the target post")
# 
# # Then, get what those users like (just 5 posts per user to keep it manageable)
# community_likes = get_multiple_profiles_likes_df(
#     profile_ids=likers,
#     total_posts_per_profile=5,
#     include_text=False
# )
# 
# # Display results
# print(f"Extracted {len(community_likes)} likes from the community")
# print(community_likes[["profile_handle", "url"]].head())

# Example 5: Find users that reference user doesn't follow
# ----------------------------------------------
# # Get users who liked a post
# post_url = "https://bsky.app/profile/bsky.app/post/3kl5q7qhny22l"
# likers = extract_post_likers(post_url, max_likers=50)
# 
# # Filter to only users not followed by the reference account
# reference_user = "your.handle.bsky.social"
# unfollowed_users = get_unfollowed_users(reference_user, likers)
# 
# print(f"Found {len(unfollowed_users)} users who liked the post but aren't followed by {reference_user}")
# for user in unfollowed_users[:5]:  # Show first 5
#     print(f"User: {user['handle']} ({user.get('displayName', 'No display name')})")
# 
# # You could then follow these users or analyze their content
