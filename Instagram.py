import requests
import re
import logging
import time
import json

module_logger = logging.getLogger('instagram')
mysql_logger = logging.getLogger('mysql')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s: %(message)s')
module_logger.setLevel(logging.INFO)
mysql_logger.setLevel(logging.DEBUG)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
module_logger.addHandler(ch)
mysql_logger.addHandler(ch)

def extract_tags(caption):
    tags = []
    for m in re.finditer('#([^\s]+)', caption):
        tags.append(m.group(1))
    return tags

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
        result['media_count'] = user['media']['count']
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
        module_logger.info('Scraping successful with ' + str(result['follower']) + ' followers and ' + str(len(result['media'])) +
                           ' posts for \'' + result['user_username'] + '\'.')
    else:
        module_logger.error('Failed to extract meta-information from HTML page')

    return result

def persist(result, mysql_cnx):
    # Step 1: get profile id from existing database record
    query = ("SELECT id FROM profiles WHERE network='instagram' AND profile_name=%s")
    cursor = mysql_cnx.cursor()
    cursor.execute(query, (result['user_username'], ))
    profile = cursor.fetchone()

    if profile is None:
        module_logger.error('No matching profile found for the given result object')
        return -1

    # Step 2: insert new profile stats record
    insert_query = ("INSERT INTO profile_stats (profile, followers, follows, posts) VALUES (%s, %s, %s, %s)")
    cursor.execute(insert_query, (profile[0], result['follower'], result['follows'], result['media_count']))

    # Step 3: iterate over all posts
    for post in result['media']:
        query = ("SELECT id FROM posts WHERE profile=%s AND osn_id=%s")
        cursor.execute(query, (profile[0], post['id']))
        row = cursor.fetchone()

        if row is None:
            # if a new post record has been created...
            insert_query = ("INSERT INTO posts "
                            "(profile, osn_id, creation, thumbnail_src, display_src, is_video, caption) "
                            "VALUES "
                            "(%s, %s, %s, %s, %s, %s, %s)")
            time_struct = time.gmtime(post['date'])
            time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
            cursor.execute(insert_query, (profile[0], post['id'], time_formatted, post['thumbnail'], post['image'], post['is_video'], post['caption']))
            post_id = cursor.lastrowid
            mysql_logger.debug('Created new post record with id ' + str(post_id))

            # and also insert and link tag records
            for tag in post['tags']:
                # check if tag name already exists in database
                query = ("SELECT id FROM tags WHERE label=%s")
                cursor.execute(query, (tag, ))
                tag_row = cursor.fetchone()
                if tag_row is None:
                    insert_query = ("INSERT INTO tags (label) VALUES (%s)")
                    cursor.execute(insert_query, (tag, ))
                    tag_id = cursor.lastrowid
                    mysql_logger.debug('Created new record for tag \'#' + tag + '\' with id ' + str(tag_id))
                else:
                    tag_id = tag_row[0]
                    mysql_logger.debug('Found existing record for tag \'#' + tag + '\'')

                # link tag to post
                insert_query = ("INSERT INTO posts_tags_mm (post_id, tag_id) VALUES (%s, %s)")
                cursor.execute(insert_query, (post_id, tag_id))
        else:
            post_id = row[0]
            mysql_logger.debug('Found existing post with id ' + str(post_id))

        # insert new post stats record
        insert_query = ("INSERT INTO post_stats (post, comments, likes) VALUES (%s, %s, %s)")
        cursor.execute(insert_query, (post_id, post['comments'], post['likes']))

    # Make sure everything is committed
    mysql_cnx.commit()
    cursor.close()