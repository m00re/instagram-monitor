import Instagram
import logging
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

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

logger = logging.getLogger('app')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s: %(message)s')
logger.setLevel(logging.INFO)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

def scrape():
    logger.info('Starting to scrape...')
    Instagram.scrape('lefrogfotografie')
    logger.info('...finished!')

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(scrape, 'interval', minutes=5)
    app.run()