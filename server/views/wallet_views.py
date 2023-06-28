from flask import (
    Blueprint,
    jsonify,
    render_template
)
from server.forms import (
    LoginForm,
    SignUpForm,
)
from server import login_manager
from server.models import User

bp = Blueprint('wallet', __name__, url_prefix='/')

@bp.route('/my_wallet/', methods=['GET'])
def my_wallet():
    '''코인 지갑 화면'''
    return render_template(
        'my_wallet.html',
    )
