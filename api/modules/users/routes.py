from flask import Blueprint, render_template, request
from api import db as mongo, authentication
from api.modules.utils import errors
from api.modules.utils.utility import Utility
import json

users_mod = Blueprint('users', __name__, url_prefix='/users')

@users_mod.before_request
def authenticate_request():
    auth_res, status_code = authentication.authenticate(request)
    if auth_res != True:
        return json.dumps( {'error': 'Invalid API access', 'message': 'Check status code.'} ), status_code, {'content-type': 'application/json'}


@users_mod.route('/', methods=['GET', 'POST'])
def get_post_users():
    if request.method == 'GET':
        users = mongo.db.users.find({ 'client_id':  request.headers['client_id'] }, {'client_id': 0})
        return json.dumps({'results': list(users)}), 200, {'content-type': 'application/json'}
        
    elif request.method == 'POST':
        sdata = request.json        
        if not request.headers.get('content-type') == 'application/json':
            return json.dumps( {'error': 'Invalid request', 'message': 'Content-type is invalid'} ), 400, {'content-type': 'application/json'}
        
        try:
            restaurant = mongo.db.restaurants.find_one({'_id': sdata['restaurant_id'], 'client_id':  request.headers['client_id']})
            if restaurant is None:
                raise errors.RestaurantDoesntExistError

            new_user = {
                '_id': Utility.generate_uuid(),
                'username': sdata['username'],
                'password': sdata['password'],
                'restaurant': restaurant['name'],
                'restaurant_info':'/restaurants/%s' % restaurant['_id'],
                'client_id':  request.headers['client_id']
            }
            mongo.db.users.insert(new_user)
            return json.dumps(new_user), 201, {'content-type': 'application/json'}
        except KeyError:
            return json.dumps( {'error': 'Invalid request', 'message': 'Invalid fields sent'} ), 400, {'content-type': 'application/json'}
        except errors.RestaurantDoesntExistError:
            return json.dumps( {'error': 'Restaurant does not exist', 'message': 'Restaurant ID does not exist for this client'} ), 404, {'content-type': 'application/json'}


@users_mod.route('/<usr_id>', methods=['GET', 'PUT', 'DELETE'])
def get_update_users(usr_id):
    user = mongo.db.users.find_one({'_id': usr_id, 'client_id': request.headers['client_id']}) # kako klijente izvesti moze li jedan restoran biti na više klijenata
    if user is None:
        return json.dumps( {'error': 'User does not exist', 'message': 'User ID for this client not found'} ), 404, {'content-type': 'application/json'}

    if request.method == 'GET':
        if user is None:
            return json.dumps({'results': []}), 404, {'content-type': 'application/json'}
        return json.dumps({'results': [ user ]}), 200, {'content-type': 'application/json'}       
    
    elif request.method == 'PUT':
        sdata = request.json
        
        if not request.headers.get('content-type') == 'application/json':
            return json.dumps( {'error': 'Invalid request', 'message': 'Content-type is invalid'} ), 400, {'content-type': 'application/json'}

        try:
            restaurant = mongo.db.restaurants.find_one({'_id': sdata['restaurant_id'], 'client_id':  request.headers['client_id']})
            if restaurant is None:
                raise errors.RestaurantDoesntExistError

            updated_user = {
                '_id': usr_id,
                'username':sdata['username'],
                'password':sdata['password'],
                'restaurant': restaurant['name'],
                'restaurant_info':'/restaurants/%s' % restaurant['_id'],
                'client_id':  request.headers['client_id']
            }
            mongo.db.users.update_one({'_id': usr_id}, {'$set': updated_user})
            return json.dumps(updated_user), 200, {'content-type': 'application/json'}
        except KeyError:
            return json.dumps( {'error': 'Invalid request', 'message': 'Invalid fields sent'} ), 400, {'content-type': 'application/json'}
        except errors.RestaurantDoesntExistError:
            return json.dumps( {'error': 'Restaurant does not exist', 'message': 'Restaurant ID does not exist for this client'} ), 404, {'content-type': 'application/json'}
    elif request.method == 'DELETE':
        mongo.db.users.remove({'_id': usr_id})
        return '', 204
