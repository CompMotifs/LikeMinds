import sys
import os
# Add the parent directory to path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from likemind.api.bluesky_api import extract_post_likers, get_multiple_profiles_likes_df



def get_seed_accounts(url):
    '''
    Return handles of users who liked the linked post.
    '''
    liker_dict = extract_post_likers(post_url = url, max_likers = 1000, rate_limit_delay = 1)
    liker_handles = []
    for user in liker_dict:
        if 'handle' in user and user['handle']:
            liker_handles.append(user['handle'])
    print(liker_handles)

#get_seed_accounts('https://bsky.app/profile/cianodonnell.bsky.social/post/3ll7v4czwzc25')

def likes_from_handles(list_of_handles):
    multiple_likes = get_multiple_profiles_likes_df(
        profile_ids=list_of_handles,
        total_posts_per_profile=1000,
        include_text=True)
    return multiple_likes[['profile_id','url','text']]

#print(likes_from_handles(['natureneuro.bsky.social','achterbrain.bsky.social']))
