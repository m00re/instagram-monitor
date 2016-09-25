import requests
import json
import re
import sqlite3

# Open SQLite database and create cursor object
conn = sqlite3.connect('stats.db')
c = conn.cursor()

# Database will have the following tables:
#
# profiles:
#   id: number
#   name: text
#
# profile_stats:
#   timestamp: number
#   followers: number
#   posts: number
#
# posts:
#   id: number
#   creation: number
#   thumbnail_src: text
#   display_src: text
#   is_video: number
#   caption: text
#
# post_stats:
#   timestamp: number
#   comments: number
#   likes: number

# Perform HTTP GET Request for Instagram profile
r = requests.get('https://www.instagram.com/lefrogfotografie/')

# Extract shared data Javascript object
data_search = re.search('<script type="text/javascript">window._sharedData = (.*);</script>', r.text, re.IGNORECASE)
if data_search:
    tmp = data_search.group(1)
    data = json.loads(tmp)
    user = data['entry_data']['ProfilePage'][0]['user']
    user_id = user['id']
    user_username = user['username']
    follower_count = user['followed_by']['count']
    media = user['media']
    media_count = media['count']

    print ('Instagram Stats for profile \'', user_username, '\'')
    print ('-- ID:', user_id)
    print ('-- Followers:', follower_count)
    print ('-- Posts:', media_count, '\n')

    print ('Got following media:')
    for post in media['nodes']:
        post_id = post['id']
        post_date = post['date']
        post_comments = post['comments']['count']
        post_likes = post['likes']['count']
        post_is_video = post['is_video']
        post_caption = post['caption']
        post_thumbnail = post['thumbnail_src']
        post_image = post['display_src']
        print ('-- ID:', post_id)
        print ('-- Date:', post_date)
        print ('-- Comments:', post_comments)
        print ('-- Likes:', post_likes, '\n')