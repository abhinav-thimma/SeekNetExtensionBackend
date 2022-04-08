from multiprocessing import connection
from flask import Flask, jsonify, request
from flask_cors import CORS
import html
import db_handler
import urllib
import os
import json

app = Flask(__name__)
CORS(app)


# if a file named 'config.json' exists in the same directory as this file, load the flask app config from it
if os.path.isfile('config.json'):
    with open('config.json') as config_file:
        app.config.update(json.load(config_file))

connection_string = app.config['CONNECTION_URL']
db_name = app.config['DB_NAME']
client = db_handler.Client(connection_string, db_name)

@app.route('/', methods=['GET'])
def getConnections():
    '''
    Called when user loads the extension in browser, returns list of questions based on tab URL
    '''
    url = request.args['url']
    ip_address = request.remote_addr
    
    client.log_action(ip_address, 'VIEW CONNECTIONS', {'src_url': url})

    connections, status = client.get_connections(url)

    return jsonify({'status': status, 'payload': {'connections': connections}})


@app.route('/connect', methods=['POST'])
def createConnection():
    '''
    Called when user creates a connection
    '''
    ip_address = request.remote_addr
    text = html.escape(request.form['connection_text'])
    tgt_url = html.escape(request.form['connection_url'])
    src_url = html.escape(request.form['current_url'])

    updated_connections, status, connection_id = client.create_connection(text, src_url, tgt_url)
    if status:
        client.log_action(ip_address, 'CREATE CONNECTION', {'id': connection_id})

    return jsonify({'status': status, 'payload': {'connections': updated_connections}})


@app.route('/log', methods=['POST'])
def logClick():
    '''
    Called to record the clicks per IP address
    '''
    ip_address = request.remote_addr
    connection_id = request.form['id']
    client.log_action(ip_address, 'CLICK CONNECTION', {'id': connection_id})
    return {}


def validate_url(url):
    tokens = [urllib.parse.urlparse(url) for url in (url)]
    min_attributes = ('scheme', 'netloc')
    for token in tokens:
        if not all([getattr(token, attr) for attr in min_attributes]):
            return False
        else:
            return True

if __name__ == '__main__':
    app.run(host='0.0.0.0')