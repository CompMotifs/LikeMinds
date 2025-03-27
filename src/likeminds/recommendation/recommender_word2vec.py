import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_similar_users(df, reference_user, top_n=5):
    """
    Find users most similar to a reference user based on the content they've liked.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing columns: 'profile_id' and 'text'
    reference_user : str
        The profile ID of the reference user
    top_n : int
        Number of similar users to return
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with similar users and their similarity scores
    """
    # Step 1: Get all unique users
    all_users = df['profile_id'].unique()
    
    if reference_user not in all_users:
        raise ValueError(f"Reference user '{reference_user}' not found in the data")
    
    # Step 2: Aggregate all text by user
    user_texts = {}
    for user in all_users:
        # Combine all text for each user
        user_df = df[df['profile_id'] == user]
        combined_text = ' '.join(user_df['text'].fillna('').tolist())
        user_texts[user] = combined_text
    
    # Step 3: Create TF-IDF vectors for all users
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(list(user_texts.values()))
    
    # Step 4: Compute cosine similarity between the reference user and all other users
    reference_idx = list(user_texts.keys()).index(reference_user)
    reference_vector = tfidf_matrix[reference_idx]
    
    similarities = []
    for i, user in enumerate(user_texts.keys()):
        if user != reference_user:
            similarity = cosine_similarity(reference_vector, tfidf_matrix[i])[0][0]
            similarities.append((user, similarity))
    
    # Step 5: Sort users by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Step 6: Return top N similar users
    similar_users = similarities[:top_n]
    
    return pd.DataFrame(similar_users, columns=['profile_id', 'similarity_score'])

# Example usage:
# similar_users = find_similar_users(df, 'natureneuro.bsky.social', top_n=5)
# print(similar_users)

def get_user_interests(df, user_id):
    """
    Extract key topics/interests for a given user based on their liked content.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing columns: 'profile_id' and 'text'
    user_id : str
        The profile ID of the user
        
    Returns:
    --------
    dict
        Dictionary with top terms and their weights
    """
    # Get all texts from the user
    user_df = df[df['profile_id'] == user_id]
    
    if user_df.empty:
        raise ValueError(f"User '{user_id}' not found in the data")
    
    combined_text = ' '.join(user_df['text'].fillna('').tolist())
    
    # Define custom stopwords including social media and URL-related terms
    custom_stopwords = [
        'www', 'http', 'https', 'com', 'org', 'net', 'bsky', 'social',
        'app', 'profile', 'url', 'link', 'html', 'htm', 'php', 'asp',
        'click', 'tweet', 'post', 'like', 'share', 'follow', 'dm',
        'retweet', 'reply', 'comment', 'thread', 'timeline', 'feed',
        'pic', 'photo', 'image', 'video', 'bio', 'don', 'didn', 'll',
        've', 're', 'amp', 'gt', 'lt'
    ]
    
    # Combine with English stopwords
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    all_stopwords = list(ENGLISH_STOP_WORDS) + custom_stopwords
    
    # Extract key terms using TF-IDF
    vectorizer = TfidfVectorizer(stop_words=all_stopwords, max_features=100)
    X = vectorizer.fit_transform([combined_text])
    
    # Get the feature names (terms)
    feature_names = vectorizer.get_feature_names_out()
    
    # Get the TF-IDF scores
    scores = X.toarray()[0]
    
    # Create a dictionary of term -> score
    term_scores = dict(zip(feature_names, scores))
    
    # Sort by score (descending)
    sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top 20 terms
    return dict(sorted_terms[:20])

def find_similar_users_with_explanation(df, reference_user, top_n=5):
    """
    Find users most similar to a reference user and provide an explanation.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing columns: 'profile_id' and 'text'
    reference_user : str
        The profile ID of the reference user
    top_n : int
        Number of similar users to return
        
    Returns:
    --------
    dict
        Dictionary with similar users, their scores, and explanations
    """
    # Get similar users
    similar_df = find_similar_users(df, reference_user, top_n)
    
    # Extract key interests for the reference user
    reference_interests = get_user_interests(df, reference_user)
    
    # Prepare results
    results = {
        'reference_user': reference_user,
        'reference_interests': reference_interests,
        'similar_users': []
    }
    
    # For each similar user, add their interests
    for _, row in similar_df.iterrows():
        user = row['profile_id']
        score = row['similarity_score']
        interests = get_user_interests(df, user)
        
        results['similar_users'].append({
            'user': user,
            'similarity_score': score,
            'interests': interests
        })
    
    return results

def get_similar_users_dataframe(df, reference_user, top_n=5):
    """
    Find users most similar to a reference user and return results as a DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing columns: 'profile_id' and 'text'
    reference_user : str
        The profile ID of the reference user
    top_n : int
        Number of similar users to return
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with columns for user, similarity score, and top interests
    """
    # Get similar users
    similar_df = find_similar_users(df, reference_user, top_n)
    
    # Create results list
    results = []
    
    # For each similar user, add row with their interests
    for _, row in similar_df.iterrows():
        user = row['profile_id']
        score = row['similarity_score']
        
        # Get top interests
        interests = get_user_interests(df, user)
        # Convert top 5 interests to a comma-separated string
        top_interests = ', '.join(list(interests.keys())[:5])
        
        results.append({
            'user': user,
            'similarity_score': score,
            'top_interests': top_interests
        })
    
    # Convert to DataFrame
    return pd.DataFrame(results)
