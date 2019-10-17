from flask import Blueprint
from api import db
import json
import os

hcheck_mod = Blueprint('healthcheck', __name__, url_prefix='/health')


@hcheck_mod.route('/', methods=['GET'])
def get_status():
    status_file = os.path.abspath(os.path.join(__file__ ,"../../.."))
    status_file = os.path.join(status_file, 'STATUS.txt')

    with open(status_file, 'r') as f:
        data = json.loads(f.read())
    return json.dumps({'status:':'running', 'version':data['VERSION']}), 200
