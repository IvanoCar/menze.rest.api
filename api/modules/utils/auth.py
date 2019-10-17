from api import db as mongo

class Auth:
    def authenticate(self, request):
        try:
            client_info = mongo.db.clients.find_one( { '_id': request.headers['client_id'] })
            if client_info is None:
                return None, 401

            if request.method == 'GET':
                if not request.headers['api-key'] == client_info['api-keys']['GET']:
                    return False, 401
                return True, 200
            elif request.method in ['POST', 'PUT', 'DELETE']:
                if not request.headers['api-key'] == client_info['api-keys']['EDIT-CREATE-DELETE']:
                    return False, 401
                return True, 200
            else:
                return None, 405
        except KeyError:
            return None, 401
