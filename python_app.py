import logging
logging.basicConfig(filename="logs/firstapimongo.log", level=logging.DEBUG, format='%(asctime)s %(funcName)5s() %(levelname)s: %(lineno)d  %(message)s', datefmt='%I:%M:%S %p')

# importing remaining libraries after logging basic config thanks to logging
# not working if others are imported before basic config
from flask import Flask, jsonify, request
from pymongo import *
import json
from bson import json_util


# pymongo setup
client = MongoClient('localhost:27017')
store_db = client.store_db
store_collection = store_db.stores


def convert_to_json(data):
    logging.debug('converting the mongo data to json')
    return json.dumps(data, default=json_util.default)

stores = [
    {
        'name': 'store-1',
        'items': [
            {
                'name': 'item 1',
                'price': 15
            },
            {
                'name': 'item 2',
                'price': 20
            }
        ]
    },
    {
        'name': 'store-2',
        'items': [
            {
                'name': 'item a',
                'price': 10
            },
            {
                'name': 'item b',
                'price': 5
            }
        ]
    },
    {
        'name': 'store-3',
        'items': [
            {
                'name': 'item 1a',
                'price': 25
            }
        ]
    }
]



'''
__name__: unique name given to the app 
'''
app = Flask(__name__)

'''
methods:

POST /store data: {name:}
- create a new store with a given name

GET /store/<string:name>
- Get a store for the given name with the data

GET /store
- Get the list of all stores

POST /store/<string:name>/item
- Create an item with a specific name inside of the store

GET /store/<string:name>/item
- Get all the items in the specific store

'''

'''
home
entrypoint
'''
@app.route('/')
def home():
    logging.debug('user entered the / entrypoint')
    print "entering home"
    return "hello, flask!"

'''
return all the stores

IMP: we have to convert the converted json into a dict
json cannot be a list, but a dictionary
our stores are in the form of a list
we have to manually convert it into a dictionary
'''
@app.route('/store')
def get_all_stores():
    '''
    logging.debug('returning all stores')
    print "returning all stores"
    return jsonify({'stores': stores})
    '''
    cursor = store_collection.find()
    all_stores = []
    for store in cursor:
        all_stores.append(store)

    print all_stores
    return convert_to_json(all_stores)


'''
POST /store data: {name:}
data comes in the form of json
'''
@app.route('/store', methods=['POST'])
def create_new_store():

    # get the data from the data sent through the http
    request_data = request.get_json()
    temp_new_name = request_data['name']
    logging.debug('creating new store with supplied name: ' + temp_new_name)
    print "creating new store with name: " + temp_new_name

    temp_new_store = {
        'name': temp_new_name,
        'items': []
    }
    stores.append(temp_new_store)
    return jsonify(temp_new_store)

'''
iterate over stores searching for the given name
if found, return jsonify(found_store)
if none, return error message

IMPORTANT: the argument 'name' in the signature should match the name of the argument
in the header
in this case, name (because <string:name>)
'''
@app.route('/store/<string:name>')
def get_store_by_name(name):

    logging.debug('returning a store of requested name: ' + name)
    print "returning store by name: " + name

    for store in stores:
        if store['name'] == name:
            return jsonify(store)
    return jsonify({'message': 'the requested store by name was not found, please try with a different name'})



'''
POST /store/<string:name>/item {name:, price:}
create an item inside the store that is specified
if the name matches a name of a store inside the list of stores
we will append the list with of items of that store with the new item
if not found, return error message

IMPORTANT: the argument 'name' in the signature should match the name of the argument
in the header
in this case, name (because <string:name>)
'''
@app.route('/store/<string:name>/item', methods=['POST'])
def create_item_in_store(name):

    # get the data from the data sent through the http
    request_data = request.get_json()
    logging.debug('creating an item in a specific store: ' + name)
    print "creating item in store: " + name

    for store in stores:
        if store['name'] == name:
            temp_new_item = {
                'name': request_data['name'],
                'price': request_data['price']
            }
            store['items'].append(temp_new_item)
            return jsonify(store)
    return jsonify({'message': 'the requested store by name was not found, please try with a different name'})


'''
GET /store/<string:name>/item
returns all the items inside the store that is specified
if the name matches a store name in the stores list, return
jsonify({'items': items})
if none are found, return error message
'''
@app.route('/store/<string:name>/item')
def get_item_list(name):

    logging.debug('getting all the items inside a particular store: ' + name)
    print "returning all items in store: " + name
    '''
    for store in stores:
        if store['name'] == name:
            return jsonify(store['items'])
    return jsonify({'message': 'the requested store by name was not found, please try with a different name'})
    '''

    cursor = store_collection.find()

    for store in cursor:
        if store['name'] == name:
            logging.debug('store found, displaying items')
            print "store found, displaying items"
            return convert_to_json(store['items'])
    return jsonify({'message': 'the requested store by name was not found, please try with a different name'})

app.run(port=5010)