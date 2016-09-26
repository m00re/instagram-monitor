import Instagram
import logging
import mysql.connector
import atexit
from mysql.connector import errorcode
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# Setup logging facilities
logger = logging.getLogger('app')
schedulerlog = logging.getLogger('apscheduler.executors.default')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s: %(message)s')
logger.setLevel(logging.INFO)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
schedulerlog.addHandler(ch)

# Setup MySQL database connection
try:
    cnx = mysql.connector.connect(user='instagram',
                                  password='aj2IcPqoFmuir9MLKPB3',
                                  host='localhost',
                                  port=3306,
                                  database='instagram_monitor',
                                  use_pure=False)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        logger.error('Access denied when connecting to MySQL database.')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        logger.error('The requested database \'instagram_monitor\' does not exist.')
    else:
        logger.error(err)


def scrape():
    logger.info('Starting to scrape...')

    query = ("SELECT id, network, profile_name FROM profiles")
    cursor = cnx.cursor()
    cursor.execute(query)
    profiles = cursor.fetchall()

    for profile in profiles:

        if profile[1] == "instagram":
            logger.info('-> scraping instagram profile \'' + profile[2] + '\'...')
            result = Instagram.scrape(profile[2])
            Instagram.persist(result, cnx)

    cnx.commit()
    cursor.close()

    logger.info('...finished!')

def close_database():
    logger.info('Closing database connection')
    cnx.close()

def ctrl_c_handler(signum, frame):
    logger.info('CTRL-C received, shutting down database connection')
    close_database()

# Flask Application Setup
app = Flask(__name__)

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
    scheduler.add_job(scrape)
    scheduler.add_job(scrape, 'interval', minutes=5)
    atexit.register(close_database)
    app.run()