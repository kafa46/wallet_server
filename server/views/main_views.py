from flask import (
    Blueprint,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for
)
from server import login_manager
from server.models import User

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/', methods=['GET', 'POST'])
def home():
    '''메인 화면'''
    login_msg = request.args.get('login')
    if login_msg:
        flash(f'로그인 성공! {g.user.user_id}님 반갑습니다.')

    return render_template(
        'index.html',
    )

