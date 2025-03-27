"""
Advanced user similarity finder using semantic embedding techniques.

Provides a sophisticated method for identifying similar users based on
the semantic content of their liked or interacted posts.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class UserSimilarityFinder:
    """
    A comprehensive system for finding similar users based on content semantics.

    Leverages advanced embedding techniques to compute user similarities
    with high computational efficiency and semantic accuracy.
    """

    def __init__(
        self, model_name: str = "all-MiniLM-L6-v2", cache_dir: Optional[str] = None
    ) -> None:
        """
        Initialize the user similarity finder.

        Args:
            model_name: Sentence transformer model for semantic embeddings.
            cache_dir: Directory for persistent embedding caching.
                       If None, uses '.embeddings_cache' in the project root.
        """
        # Determine project root directory
        project_root = Path(__file__).resolve().parent.parent

        # Set cache directory
        if cache_dir is None:
            cache_dir = project_root / ".embeddings_cache"
        else:
            cache_dir = Path(cache_dir)

        # Ensure cache directory exists
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sentence transformer model
        self.model = SentenceTransformer(model_name)

    def _compute_user_embedding(self, df: pd.DataFrame, profile_id: str) -> np.ndarray:
        """
        Compute the average embedding for a user's content.

        Args:
            df: DataFrame containing user content.
            profile_id: Profile ID to compute embedding for.

        Returns:
            Averaged embedding vector for the user's content.
        """
        # Filter content for the specific user
        user_rows = df[df["profile_id"] == profile_id]

        # Combine text content to create a comprehensive user representation
        user_content = user_rows.apply(
            lambda row: f"{row['text']} {row['url']}", axis=1
        ).tolist()

        if not user_content:
            return np.zeros(self.model.get_sentence_embedding_dimension())

        # Compute embeddings for user's content
        embeddings = self.model.encode(user_content)

        # Return average embedding
        return np.mean(embeddings, axis=0)

    def find_similar_users(
        self, df: pd.DataFrame, reference_user: str, top_n: int = 5
    ) -> pd.DataFrame:
        """
        Find users most similar to a reference user based on content semantics.

        Args:
            df: DataFrame containing user profiles, content, and URLs.
            reference_user: Profile ID of the reference user.
            top_n: Number of similar users to return.

        Returns:
            DataFrame of similar users with their similarity scores and top URL.
        """
        # Validate input DataFrame
        required_columns = {"profile_id", "text", "url"}
        if not required_columns.issubset(df.columns):
            raise ValueError(
                "DataFrame must contain 'profile_id', 'text', and 'url' columns"
            )

        # Compute reference user's embedding
        reference_embedding = self._compute_user_embedding(df, reference_user)

        # Compute embeddings for all unique users
        unique_users = df["profile_id"].unique()
        user_embeddings = {
            user: self._compute_user_embedding(df, user)
            for user in unique_users
            if user != reference_user
        }

        # Compute similarities
        similarities = {
            user: float(
                cosine_similarity(
                    reference_embedding.reshape(1, -1), embedding.reshape(1, -1)
                )[0][0]
            )
            for user, embedding in user_embeddings.items()
        }

        # Create similarity DataFrame with top URLs
        similarity_df = pd.DataFrame.from_dict(
            similarities, orient="index", columns=["similarity_score"]
        ).reset_index()
        similarity_df.columns = ["profile_id", "similarity_score"]

        # Add top URL for each similar user
        def get_top_url(profile_id):
            user_urls = df[df["profile_id"] == profile_id]["url"]
            return user_urls.value_counts().index[0] if len(user_urls) > 0 else None

        similarity_df["top_url"] = similarity_df["profile_id"].apply(get_top_url)

        # Sort and return top N similar users
        return (
            similarity_df.sort_values("similarity_score", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )


# Demonstration of usage
def main() -> None:
    """Demonstrate the advanced user similarity finder."""
    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "profile_id": [
                "user1",
                "user1",
                "user2",
                "user2",
                "user3",
                "user3",
                "user4",
                "user4",
            ],
            "url": [
                "https://bluesky.com/ml1",
                "https://bluesky.com/ai1",
                "https://bluesky.com/data1",
                "https://bluesky.com/algo1",
                "https://bluesky.com/nn1",
                "https://bluesky.com/ml2",
                "https://bluesky.com/tech1",
                "https://bluesky.com/innovation1",
            ],
            "text": [
                "Machine learning is fascinating",
                "Deep learning revolutionizes AI",
                "Data science techniques are evolving",
                "AI algorithms are becoming more sophisticated",
                "Neural networks are complex systems",
                "Advanced machine learning models",
                "Technology is rapidly changing",
                "Innovative solutions drive progress",
            ],
        }
    )

    # Initialize finder
    finder = UserSimilarityFinder()

    # Find similar users
    similar_users = finder.find_similar_users(df, "user1", top_n=3)
    print("Similar Users:")
    print(similar_users)


if __name__ == "__main__":
    main()
