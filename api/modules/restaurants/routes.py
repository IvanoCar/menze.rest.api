from flask import Blueprint, render_template, request, redirect
from api import db as mongo, authentication
from api.modules.utils import errors
from api.modules.utils.utility import Utility
import time
import json


restaurants_mod = Blueprint('restaurants', __name__, url_prefix='/restaurants')

@restaurants_mod.before_request
def authenticate_request():
    auth_res, status_code = authentication.authenticate(request)
    if auth_res != True:
        return json.dumps( {'error': 'Invalid API access', 'message': 'Check status code.'} ), status_code, {'content-type': 'application/json'}

@restaurants_mod.route('/', methods=['GET', 'POST'])
def get_post_delete_users():
    
    if request.method == 'GET':
        restaurants = mongo.db.restaurants.find({ 'client_id':  request.headers['client_id'] })
        return json.dumps({'results': list(restaurants)}), 200, {'content-type': 'application/json'}
    
    elif request.method == 'POST':
        sdata = request.json
        
        if not request.headers.get('content-type') == 'application/json':
            return json.dumps( {'error': 'Invalid request', 'message': 'Content-type is invalid'} ), 400, {'content-type': 'application/json'}
        try:
            nid = Utility.generate_uuid()
            new_restaurant = {
                '_id': nid,
                "name": sdata['name'],
                "address": sdata['address'],
                "city": sdata['city'].capitalize(),
                "postal_code": sdata['postal_code'],
                "food_data": "/restaurants/%s/food" % nid,
                "client_id": request.headers['client_id']
            }
            mongo.db.restaurants.insert(new_restaurant)
            mongo.db.food.insert( {'restaurant_id': nid, 'data': {} } )
            
            return json.dumps(new_restaurant), 201, {'content-type': 'application/json'}
        except KeyError:
            return json.dumps( {'error': 'Invalid request', 'message': 'Invalid fields sent'} ), 400, {'content-type': 'application/json'}


@restaurants_mod.route('/<rest_id>', methods=['GET', 'PUT', 'DELETE'])
def get_update_delete_restaurants(rest_id):

    restaurant = mongo.db.restaurants.find_one({'_id': rest_id, 'client_id':  request.headers['client_id']})
    if restaurant is None:
        return json.dumps( {'error': 'Restaurant does not exist', 'message': 'Restaurant ID not found'} ), 404, {'content-type': 'application/json'}
   
    if request.method == 'GET':
        if restaurant is None:
            return json.dumps({'results': []}), 404, {'content-type': 'application/json'}
        return json.dumps({'results': [ restaurant ]}), 200, {'content-type': 'application/json'}       
    
    elif request.method == 'PUT':
        sdata = request.json
        
        if not request.headers.get('content-type') == 'application/json':
            return json.dumps( {'error': 'Invalid request', 'message': 'Content-type is invalid'} ), 400, {'content-type': 'application/json'}

        try:
            updated_restaurant = {
                '_id': rest_id,
                "name": sdata['name'],
                "address": sdata['address'],
                "city": sdata['city'].capitalize(),
                "postal_code": sdata['postal_code'],
                "food_data": "/restaurants/%s/food" % rest_id,
                'client_id':  request.headers['client_id']
            }
            mongo.db.restaurants.update_one({'_id': rest_id}, {'$set': updated_restaurant})
            return json.dumps(updated_restaurant), 200, {'content-type': 'application/json'}
        except KeyError:
            return json.dumps( {'error': 'Invalid request', 'message': 'Invalid fields sent'} ), 400, {'content-type': 'application/json'}
    elif request.method == 'DELETE':
        mongo.db.restaurants.remove({'_id': rest_id})
        mongo.db.food.remove({'restaurant_id': rest_id})
        mongo.db.stats.remove({'restaurant_id': rest_id})
        return '', 204

# -------------------------------------------------------------------------------------------------FOOD
@restaurants_mod.route('/<rest_id>/food', methods=['GET', 'PUT'])
def get_update_food_by_restid(rest_id):

    restaurant = mongo.db.restaurants.find_one({'_id': rest_id, 'client_id':  request.headers['client_id']})
    if restaurant is None:
        return json.dumps( {'error': 'Restaurant does not exist', 'message': 'Restaurant ID not found'} ), 404, {'content-type': 'application/json'}
   
    if request.method == 'GET':
        if restaurant is None:
            return json.dumps({'results': []}), 404, {'content-type': 'application/json'}
        
        fdata = mongo.db.food.find_one( {'restaurant_id': rest_id} )
        if not fdata['data']:
            return json.dumps({'results': fdata['data']}), 404, {'content-type': 'application/json'}       

        return json.dumps({'results': fdata['data']}), 200, {'content-type': 'application/json'}       
    
    elif request.method == 'PUT':        
        if not request.headers.get('content-type') == 'application/json':
            return json.dumps( {'error': 'Invalid request', 'message': 'content-type is invalid'} ), 400, {'content-type': 'application/json'}

        sdata = json.loads(request.json)
        try:
            updated_restaurant_food = {
                'restaurant_id': rest_id,
                'data': sdata['food_data']
            }
            mongo.db.food.update_one({'restaurant_id': rest_id}, {'$set': updated_restaurant_food})
            
            #---------------------------------------------------------------------------------------------
            date = time.strftime('%d/%m/%Y')

            stats = mongo.db.stats.find_one({'restaurant_id': rest_id, 'date': date})
            if stats is None:
                new =  {'restaurant_id': rest_id, 'count': 1, 'date': date }
                mongo.db.stats.insert(new)
            else:
                c = stats['count']
                update = {
                    "restaurant_id": rest_id,
                    "date": date,
                    "count": c + 1
                }
                mongo.db.stats.update_one({'restaurant_id': rest_id}, {'$set': update})
            return json.dumps(updated_restaurant_food), 200, {'content-type': 'application/json'}
        except KeyError:
            return json.dumps( {'error': 'Invalid request', 'message': 'Invalid fields sent'} ), 400, {'content-type': 'application/json'}

@restaurants_mod.route('/multiple', methods=['GET'])
def redirect_multiple():
    return redirect('/restaurants')


@restaurants_mod.route('/multiple/<rest_ids>', methods=['GET'])
def get_mutiple_restaurants(rest_ids):
    if not '+' in rest_ids:
        return json.dumps( {'error': 'Invalid request', 'message': 'Seperate multiple ids with +'} ), 400, {'content-type': 'application/json'}
    
    rest_ids = rest_ids.split('+')
    # ogranicenje na broj restorana? SHOULD return 414 (Request-URI Too Long)
    errors = []
    results = []
    return_dict = {}

    for rid in rest_ids:
        if len(rid) == 0:
            continue
        restaurant = mongo.db.restaurants.find_one({'_id': rid, 'client_id':  request.headers['client_id']})
        if restaurant is None:
            errors.append(rid)
            continue
        results.append(restaurant)

    return_dict['has_errors'] = False
    return_dict['errors'] = {}

    if len(errors) > 0:
        return_dict['has_errors'] = True
        return_dict['errors']['count'] = len(errors)
        return_dict['errors']['restaurants'] = errors
    return_dict['results'] = results
    
    return json.dumps(return_dict), 200, {'content-type': 'application/json'}


@restaurants_mod.route('/multiple/<rest_ids>/food', methods=['GET'])
def get_mutimple_restaurants_food(rest_ids):
    if not '+' in rest_ids:
        return json.dumps( {'error': 'Invalid request', 'message': 'Seperate ids with +'} ), 400, {'content-type': 'application/json'}
    
    rest_ids = rest_ids.split('+')
    # ogranicenje na broj restorana? SHOULD return 414 (Request-URI Too Long)
    errors = []
    results = []
    return_dict = {}

    for rid in rest_ids:
        if len(rid) == 0:
            continue
        restaurant = mongo.db.restaurants.find_one({'_id': rid, 'client_id':  request.headers['client_id']})
        if restaurant is None:
            errors.append(rid)
            continue
        fdata = mongo.db.food.find_one( {'restaurant_id': rid} )
        results_el = {
            'restaurant_id' : restaurant['_id'],
            'restaurant_name' : restaurant['name'],
            'food_data': fdata['data']
        }
        results.append(results_el)

    return_dict['has_errors'] = False
    return_dict['errors'] = {}

    if len(errors) > 0:
        return_dict['has_errors'] = True
        return_dict['errors']['count'] = len(errors)
        return_dict['errors']['restaurants'] = errors
    return_dict['results'] = results
    
    return json.dumps(return_dict), 200, {'content-type': 'application/json'}

# ------------------------------------------------------------------------------------ STATS

@restaurants_mod.route('/<rest_id>/analytics', methods=['GET', 'PUT'])
def get_update_nuber_of_updates_by_restid(rest_id):

    date = time.strftime('%d/%m/%Y')

    stats = mongo.db.stats.find({'restaurant_id': rest_id}, {'_id': 0})
    
    if request.method == 'GET':
        return json.dumps({'results': list(stats)}), 200, {'content-type': 'application/json'}       
