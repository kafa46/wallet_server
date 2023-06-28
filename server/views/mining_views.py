from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    flash,
)
from flask_wtf.csrf import generate_csrf
import requests
from server.forms import (
    TransferForm,
)
from server import login_manager
from server import csrf
from server.wallet import Wallet
from server.models import User

bp = Blueprint('mine', __name__, url_prefix='/')

BLOCKCHAIN_NEIGHBOR='http://203.252.240.43:7000/transactions/'

@bp.route('/mining_home/', methods=['GET'])
@csrf.exempt
def mining_home():
    return render_template(
        'mining.html',
    )