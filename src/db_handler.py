import pymongo
import time


class Client:
    def __init__(self, connection_string, database):
        self.connections = pymongo.MongoClient(connection_string)[database]['extension_connections']
        self.logging = pymongo.MongoClient(connection_string)[database]['extension_actions']


    def log_action(self, ip_address, action, data):
        '''
        Used to store user actions like clicks to monogoDB.
        '''
        try:
            self.logging.insert_one({'ip_address': ip_address,
                                     'time': time.time(),
                                     'action': action,
                                     'data': data
                                     })
            return True
        except Exception as e:
            print('Error logging action: ', e)
            return False

    def get_connections(self, url):
        '''
        Fetches all connections having src_url as url from `extension_connections` collection in mongodb.
        '''
        results = []
        try:
            cursor = self.connections.find({'src_url': url})
            for conn in cursor:
                conn['_id'] = str(conn['_id'])
                results.append(conn)
            return results, 1
        except Exception as e:
            print('Error getting connections :', e)
            return results, 0


    def create_connection(self, text, src_url, tgt_url, target_title=None, target_body=None):
        '''
        Creates a connection in `extension_connections` collection in mongodb.
        '''
        try:
            connection_id = self.connections.insert_one({"time": time.time(),
                                     "src_url": src_url,
                                     "tgt_url": tgt_url,
                                     "text": text,
                                     "target_title": target_title,
                                     "target_body": target_body
                                    }).inserted_id
            status = 1
        except Exception as e:
            print('Error creating connection: ', e )
            status = 0
            connection_id = ''

        connections, _ = self.get_connections(src_url)
        return connections, status, str(connection_id)
    
    def get_all_connections(self):
        '''
        Featches all the connections from `extension_connections` collection in mongodb.
        '''
        results = []
        try:
            cursor = self.connections.find()
            for conn in cursor:
                conn['_id'] = str(conn['_id'])
                results.append(conn)
            return results
        except Exception as e:
            print('Error getting connections :', e)
            return results
