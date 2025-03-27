# src/web/app.py

import streamlit as st
import pandas as pd

from likeminds.api.bluesky_api import ( 
    get_unfollowed_users,
)

from likeminds.web.app_functions import (
    seed_input_check, 
    get_seed_accounts, 
    likes_from_handles
)

from likeminds.recommendation.filter_science import (
    filter_posts_by_science
)

from likeminds.recommendation.recommender import (
    rank_users_by_post_overlap 
)

from likeminds.recommendation.recommender_word2vec import (
    get_similar_users_dataframe
)
# Import placeholder functions from your modules.
# These should be implemented in your repo.
# from src.api.bluesky_api import (
#     get_user_liked_posts,
#     get_seed_accounts,
#     get_user_following,
# )
# from src.recommendation.filter import add_is_scientific_column
# from src.recommendation.recommender import (
#     generate_like_fingerprint,
#     find_closest_matches,
# )

def main():
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        st.image("data/logo.png")
    with col2:
        # st.title("LikeMinds")
        st.title("LikeMinds: Find Your Circle")

    st.markdown(

        "Discover potential connections by comparing your liked posts with others, "
        "focusing on content-based filters."
    )
    
    # user_handle = st.text_input("Enter your Bluesky handle:", placeholder="@")
    user_handle = st.text_input("Enter your Bluesky handle:", value="", placeholder="@")
    # todo add check handle exists
    if ".bsky.social" not in user_handle:
        user_handle = f"{user_handle}.bsky.social"

    seed_input = st.text_area(
        "Enter a seed post URL (one post) or a comma-separated list of handles "
        "to find matches among (e.g. conference attendees):"
    )
    
    # Dropdown for potential filters
    filter_option = st.selectbox(
        "Select a content filter:",
        ["Scientific posts", "Music posts", "All posts"]
    )
    
    matching_option = st.selectbox(
        "Select a content filter:",
        ["Like overlap", "Word2Vec", "SBert"]
    )

    top_n = st.number_input("Number of recommendations", min_value=1, max_value=10, value=3)

    if st.button("Find Matches") and user_handle:

        st.info("Checking if seed input is post or handles")
        seed_result = seed_input_check(seed_input)
        if not seed_result["valid"]:
            st.error(seed_result["error"])
            st.stop()  # Halt further execution until the user corrects the input

        if seed_result["type"] == "url":
            # Should be list
            st.info("Getting seed accounts from URL...")
            seed_accounts = get_seed_accounts(seed_result["value"])
        else: 
            seed_accounts = seed_result["value"]
        st.info(seed_accounts)
            

        # todo remove
        # seed_accounts = seed_accounts[:3]

        all_handles = [user_handle] + seed_accounts

        st.info("Fetching all liked posts...")

        st.info(all_handles)

        likes_df = likes_from_handles(all_handles)

        # Your logic here can use filter_option to determine which filtering function to apply.
        # st.write(f"Using filter: {filter_option}")
        st.dataframe(likes_df)

        # Todo: add filter of users 
        st.info("Excluding accounts already followed...")
        
        # st.info("Adding user IDs and liked posts for candidate accounts...")

        if filter_option == "Scientific posts":
            st.info("Keeping only scientific posts...")
            filtered_df = filter_posts_by_science(likes_df)
        
        elif filter_option == "All posts":
            
            st.info("Keeping all posts...")
            filtered_df = likes_df

        st.dataframe(filtered_df)

        removed_df = likes_df[~likes_df['url'].isin(filtered_df['url'])]

        st.subheader("Posts Removed by Filtering")
        

        if not removed_df.empty:
            st.write("The following posts were removed:")
            # Display only the "text" column for each removed post
            st.dataframe(removed_df[['text']])
        else:
            st.info("No posts were removed based on the current filter.")

        st.info("Finding closest matching fingerprints...")

        if matching_option == "Like overlap":
            st.info("Ranking users by like overlap...")
            # Call the updated function; it returns a DataFrame with match scores
            reccs_df = rank_users_by_post_overlap(
                profile_id=user_handle,
                liked_posts_df=filtered_df
            )
            if not reccs_df.empty:
                st.subheader("Recommended Matches (ordered by match score)")
                st.dataframe(reccs_df)
            else:
                st.error("No matching profiles found.")
            
        elif matching_option == "Word2Vec":
            # Call the Word2Vec-based function; it returns a DataFrame with similar users and their similarity scores
            st.dataframe(filtered_df)
            similar_users_df = get_similar_users_dataframe(
                df=filtered_df, 
                reference_user=user_handle, 
                top_n=top_n
            )

            if not similar_users_df.empty:
                st.subheader("Recommended Matches (Word2Vec/TF-IDF based)")
                st.dataframe(similar_users_df)
            else:
                st.error("No matching profiles found.")

if __name__ == "__main__":
    main()