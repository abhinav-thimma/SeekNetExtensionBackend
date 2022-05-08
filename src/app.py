from multiprocessing import connection
from flask import Flask, jsonify, request
from flask_cors import CORS
import html
import db_handler
import urllib
import os
import json
from BM25 import BM25
from ddg_api import ddg_search


LOG_TO_CONN_THRESHOLD = 2

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
    Called when user loads the extension in browser.
    Returns: list of previously made connections based on tab URL
    '''
    url = request.args['url']
    ip_address = request.remote_addr
    
    print('Viewed connections for: ', url)

    connections, status = client.get_connections(url)
    print(connections)
    return jsonify({'status': status, 'payload': {'connections': connections}})

@app.route('/ddg', methods=['GET'])
def getDDGResults():
    '''
    Called when user searches for a query in extension. This API calls the DuckDuckGo search API.
    Returns: list of search results from DuckDuckGo
    '''
    query_words = request.args['query']
    ddg_results = ddg_search(query_words)

    return jsonify({'results': ddg_results})


@app.route('/connect', methods=['POST'])
def createConnection():
    '''
    Called when user creates a connection
    Returns: status of connection creation
    '''
    ip_address = request.remote_addr
    req = request.get_json()
    text = req['text']
    src_url = req['src_url']
    tgt_url = req['tgt_url']
    print(f'Text: {text}, Source URL: {src_url}, Target URL: {tgt_url}')

    updated_connections, status, connection_id = client.create_connection(text, src_url, tgt_url)
    if status:
        client.log_action(ip_address, 'CREATE CONNECTION', {'id': connection_id})

    return jsonify({'status': status, 'payload': {'connections': updated_connections}})

@app.route('/search', methods=['POST'])
def search():
    '''
    Called from front end when user searches in context of a url
    Returns: list of search results from database
    '''
    req = request.get_json()
    query = req['query']
    url = req['url']
    print(f'Query: {query}')
    
    bm25 = BM25(client)
    results = bm25.search(query)

    # preprocessing the results
    results = [{'url': result['tgt_url'], 'text': result['text'], 'id': result['_id']} for result in results]
    return {'results': results, 'count': len(results)}

@app.route('/log_clicks', methods=['POST'])
def log_clicks():
    '''
    Called from front end when user clicks on a connection. Log conenctions for creating connections automatically.
    Returns: None
    '''
    ip_address = request.remote_addr
    req = request.get_json()
    src_url = req['src_url']
    tgt_url = req['tgt_url']
    search_text = req['search_text']

    print(f'Logging Click | Src URL: {src_url}, Tgt URL: {tgt_url}, Search Text: {search_text}')

    results = client.get_clicks_with_matching_urls(src_url, tgt_url)
    if(len(results) >= LOG_TO_CONN_THRESHOLD):
        text = max([r['search_text'] for r in results], key = len) if(search_text is None or len(search_text) == 0) else search_text
        client.create_connection(text, src_url, tgt_url)

    client.log_action(ip_address, 'CLICK LINK', {'src_url': src_url, 'tgt_url': tgt_url, 'search_text': search_text})
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