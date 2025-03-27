# src/web/app.py

import streamlit as st
import pandas as pd

from likeminds.web.app_functions import (
    seed_input_check, 
    get_seed_accounts, 
    likes_from_handles
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

    seed_input = st.text_area(
        "Enter a seed post URL (one post) or a comma-separated list of handles "
        "to find matches among (e.g. conference attendees):"
    )
    
    # Dropdown for potential filters
    filter_option = st.selectbox(
        "Select a content filter:",
        ["Scientific posts", "Music posts", "All posts"]
    )
    
    top_n = st.number_input("Number of recommendations", min_value=1, max_value=10, value=3)

    if st.button("Find Matches") and user_handle:

        seed_result = seed_input_check(seed_input)
        if not seed_result["valid"]:
            st.error(seed_result["error"])
            st.stop()  # Halt further execution until the user corrects the input

        st.info("Fetching your liked posts...")

        # Your logic here can use filter_option to determine which filtering function to apply.
        st.write(f"Using filter: {filter_option}")

        st.info("Generating DataFrame for user's liked posts...")

        st.info("Checking if seed input is post or handles")

        st.info("Excluding accounts already followed...")

        st.info("Adding user IDs and liked posts for candidate accounts...")

        st.info("Including filtering columns (e.g., 'is_scientific')...")

        st.info("Generating like fingerprints for user and candidates...")

        st.info("Finding closest matching fingerprints...")
        
        # Render pandas df at end


        # Continue with the fetching, filtering, and recommendation process.
        # # Generate user's liked posts DataFrame
        # user_likes_df = get_user_liked_posts(user_handle)
        # # Add filtering column (e.g. whether the post is scientific)
        # user_likes_df = add_is_scientific_column(user_likes_df, text_column="content")
        # st.write("Your Liked Posts", user_likes_df)
        
        # if seed_input:
        #     seed_input = seed_input.strip()
        #     # Determine if seed input is a post ID or a list of handles
        #     if "," in seed_input:
        #         seed_handles = [h.strip() for h in seed_input.split(",")]
        #     else:
        #         # Assume seed input is a post ID; fetch accounts who liked this post
        #         seed_handles = get_seed_accounts(seed_input)
            
        #     # Remove accounts the user already follows
        #     following = get_user_following(user_handle)
        #     candidate_handles = [h for h in seed_handles if h not in following]
        #     st.write("Candidate accounts (after filtering out those you already follow):", candidate_handles)
            
        #     # For each candidate, get their liked posts and build a combined DataFrame
        #     candidate_dfs = []
        #     for handle in candidate_handles:
        #         df = get_user_liked_posts(handle)
        #         df["user_handle"] = handle
        #         df = add_is_scientific_column(df, text_column="content")
        #         candidate_dfs.append(df)
            
        #     if candidate_dfs:
        #         all_candidates_df = pd.concat(candidate_dfs, ignore_index=True)
        #         st.write("Candidate Liked Posts", all_candidates_df)
                
        #         # Generate like fingerprints
        #         user_fp = generate_like_fingerprint(user_likes_df)
        #         candidate_fps = {}
        #         for handle in candidate_handles:
        #             candidate_df = all_candidates_df[all_candidates_df["user_handle"] == handle]
        #             candidate_fps[handle] = generate_like_fingerprint(candidate_df)
                
        #         # Find closest matching fingerprints
        #         recommendations = find_closest_matches(user_fp, candidate_fps, top_n)
        #         st.subheader("Top Recommended Accounts")
        #         st.write(recommendations)
        #     else:
        #         st.warning("No candidate accounts found from the provided seed input.")
        # else:
        #     st.warning("Please provide a seed post ID or a list of handles to search for matches.")

if __name__ == "__main__":
    main()