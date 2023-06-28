from datetime import datetime
from flask import (
    flash,
    g,
    redirect,
    request,
    Blueprint,
    jsonify,
    render_template,
    session,
    url_for
)
from werkzeug.security import generate_password_hash, check_password_hash
from server import login_manager
from server import db
from server.forms import LoginForm, SignUpForm
from server.models import User
from server.wallet import Wallet
from server.utils.sanitizer_utils import sanitize_json_or_dict
from server.utils.passwd_utils import check_passwd_strength

bp = Blueprint('auth', __name__, url_prefix='/')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    '''User 로그인'''
    form = LoginForm()
    sign_up_status = request.args.get('sign_up')

    if sign_up_status:
        flash('회원가입에 성공하였습니다.')

    if request.method=='POST' and form.validate_on_submit():
        data_dic = sanitize_json_or_dict(request.form.to_dict())
        user_id = data_dic.get('user_id')
        passwd = data_dic.get('passwd')
        user = User.query.filter_by(user_id=user_id).first()

        if not user:
            flash("존재하지 않는 사용자 입니다.")
            return render_template('login.html', form=form)

        if not check_password_hash(user.passwd, passwd):
            flash('비밀번호가 맞지 않습니다.')
            return render_template('login.html',form=form)

        flash(f'로그인 성공! {user.user_id}님 반갑습니다 ^^.')
        session.clear()
        session['user_id'] = user.user_id
        session['user_key'] = user.id
        return redirect(url_for('main.home', login='success'))

    return render_template(
        'login.html',
        form=form,
    )


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.home'))


@bp.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    '''User 회원가입'''
    form = SignUpForm()
    if request.method=='POST' and form.validate_on_submit():
        data_dic = sanitize_json_or_dict(request.form.to_dict())
        user_id = data_dic.get('user_id')
        print(f'user_id: {data_dic.get(user_id)}' )
        user = User.query.filter_by(user_id=user_id).first()
        error = None

        if user:
            error = '이미 존재하는 아이디입니다.'
            flash(error)
            return render_template('sign_up.html', form=form)

        passwd_check_result = check_passwd_strength(data_dic.get('passwd1'))
        if passwd_check_result is not True:
            flash(passwd_check_result)
            return render_template('sign_up.html', form=form)

        ### 사용자 검증에 성공한 경우 ###
        # Wallet 객체 생성 -> private, public, blockchain address
        wallet = Wallet()

        # DB 입력
        user = User(
            user_id = user_id,
            passwd = generate_password_hash(data_dic.get('passwd1')),
            email = data_dic.get('email'),
            phone_mobile = data_dic.get('phone_mobile'),
            name = data_dic.get('name'),
            create_date = datetime.now(),
            update_date = datetime.now(),
            private_key = wallet.private_key,
            public_key = wallet.public_key,
            blockchain_addr = wallet.blockchain_address
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login', sign_up='success'))

    return render_template(
        'sign_up.html',
        form=form,
    )


@bp.before_app_request
def load_logged_in_user():
    user_key = session.get('user_key')
    if user_key is None:
        g.user = None
    else:
        g.user = User.query.get(user_key) # 사용자 Primary Key 등록