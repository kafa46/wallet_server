import config
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
from server.p2p_manager import P2PManager

bp = Blueprint('transfer', __name__, url_prefix='/')

BLOCKCHAIN_NEIGHBOR='http://203.252.240.43:7000/transactions/'

@bp.route('/transfer/', methods=['GET', 'POST'])
@csrf.exempt
def transfer():
    '''코인 이체 화면'''
    form = TransferForm()

    if request.method=='POST' and form.validate_on_submit():
        send_blockchain_addr = request.form.get('send_addr')
        amount = float(request.form.get('amount'))
        if amount is None:
            flash('이체할 코인 수량을 입력하셔야 합니다.')
            return render_template('transfer.html', form=form)

        send_private_key = request.form.get('private_key')
        if send_private_key is None:
            flash('이체를 위해서는 반드시 본인의 비밀키를 입력해야 합니다.')
            return render_template('transfer.html', form=form)

        send_public_key = request.form.get('public_key')
        if send_public_key is None:
            flash('이체를 위해서는 반드시 본인의 공개키를 입력해야 합니다.')
            return render_template('transfer.html', form=form)

        recv_blockchain_addr = request.form.get('recv_addr')
        if recv_blockchain_addr is None:
            flash('받는사람 지갑 주소가 없습니다.')
            return render_template('transfer.html', form=form)

        signature = Wallet.generate_signature(
            send_blockchain_addr,
            recv_blockchain_addr,
            send_private_key,
            amount,
        )

        print(f'signature: {signature}')

        json_data = {
            'send_public_key': send_public_key,
            'send_blockchain_addr': send_blockchain_addr,
            'recv_blockchain_addr': recv_blockchain_addr,
            'amount': amount,
            'signature': signature,
        }
        # csrf token issue: INFO:flask_wtf.csrf:The CSRF token is missing.
        #   ref1: https://stackoverflow.com/questions/29899686/how-do-i-pass-a-csrf-token-using-the-python-requests-library
        #   ref2: https://stackoverflow.com/questions/57647321/obtain-csrf-token-and-assign-to-variable

        hedaders = {
            'X-CSRFToken': generate_csrf()
        }

        # 현재 연결된 노드의 접속 주소 가져오기
        p2p_manager = P2PManager()
        neighbor = p2p_manager.get_one_active_node() # 한개 노드만 가져오기
        print(f'neighbor: {neighbor.ip}:{neighbor.port}')

        neighbor_addr =  f'http://{neighbor.ip}:{config.BLOCKCHAIN_PORT}/transactions/'
        # neighbor_addr = 'http://203.252.240.46:7000/transactions'
        print(f'neighbor_addr: {neighbor_addr}')
        response = requests.post(
            neighbor_addr,
            json=json_data,
            timeout=3,
            headers=hedaders,
        )

        print('Trying to access to blockchain neighbor')
        if response.status_code==201:
            return jsonify({
                'status': 'success',
                'amount': amount,
            }), 201

        return jsonify({'status': 'fail'}), 400

    return render_template(
        'transfer.html',
        form=form,
    )
