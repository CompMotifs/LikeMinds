import re
import pandas as pd

def is_scientific(text: str) -> bool:
    """
    A placeholder function to identify whether a post's text 
    appears to be scientific in nature, based on simple keywords.
    
    Extend or replace this logic with more robust methods 
    (e.g., an NLP classifier) to meet your needs.
    """
    # Basic keyword-based matching
    science_keywords = [
        r'\bscience\b',
        r'\bresearch\b',
        r'\bstudy\b',
        r'\bexperiment\b',
        r'\bdata\b',
        r'\bphd\b',
        r'\bpublication\b',
        r'\bscientific\b',
        r'\blab\b',
    ]
    pattern = re.compile('|'.join(science_keywords), re.IGNORECASE)
    return bool(pattern.search(text))

def add_is_scientific_column(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Adds a boolean column 'is_scientific' to a DataFrame of posts, 
    based on the content in 'text_column'.

    :param df: DataFrame containing post data
    :param text_column: Name of the column in df that stores post text
    :return: DataFrame with a new 'is_scientific' column
    """
    df['is_scientific'] = df[text_column].apply(is_scientific)
    return df

def filter_posts_by_science(df: pd.DataFrame, keep_scientific: bool = True) -> pd.DataFrame:
    """
    Returns a subset of the DataFrame containing only scientific posts 
    (if keep_scientific=True), or non-scientific posts otherwise.

    :param df: DataFrame expected to have 'is_scientific' column
    :param keep_scientific: True => keep only 'is_scientific' == True
    :return: Filtered DataFrame
    """
    if 'is_scientific' not in df.columns:
        raise ValueError("DataFrame must have 'is_scientific' column before filtering.")
    return df[df['is_scientific'] == keep_scientific]