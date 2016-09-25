import Instagram
import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

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

# Returns a list of supported networks
@app.route('/networks', methods=['GET'])
def networks():
    return jsonify({
        'networks': [{
            'name': 'instagram',
            'href': '/profiles/instagram'
        }]
    })

# Endpoint for all known profiles on a given network
@app.route('/profiles/<string:network>', methods=['GET'])
def profiles(network):
    return jsonify({
        'href': '/profiles/' + network,
        'names': ['lefrogfotografie']
    })

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(scrape, 'interval', minutes=5)
    app.run()