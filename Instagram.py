from contextlib import contextmanager
import requests
import re
import json

def extract_tags(caption):
    tags = []
    for m in re.finditer('#([^\s]+)', caption):
        tags.append(m.group(1))
    return tags

@contextmanager
def scrape(profilename):

    # Prepare result hash
    result = { 'success': 0 }

    # Perform HTTP GET Request for Instagram profile
    r = requests.get('https://www.instagram.com/' + profilename)

    # Extract shared data Javascript object
    data_search = re.search('<script type="text/javascript">window._sharedData = (.*);</script>', r.text, re.IGNORECASE)
    if data_search:
        tmp = data_search.group(1)
        data = json.loads(tmp)
        user = data['entry_data']['ProfilePage'][0]['user']
        result['user_id'] = user['id']
        result['user_username'] = user['username']
        result['follower'] = user['followed_by']['count']
        result['follows'] = user['follows']['count']
        result['media'] = []

        for post in user['media']['nodes']:
            post = {
                'id': post['id'],
                'date': post['date'],
                'comments': post['comments']['count'],
                'likes': post['likes']['count'],
                'is_video': post['is_video'],
                'caption': post['caption'],
                'thumbnail': post['thumbnail_src'],
                'image': post['display_src'],
                'tags': extract_tags(post['caption'])
            }
            result['media'].append(post)

        result['success'] = 1

    yield result