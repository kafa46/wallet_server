from datetime import datetime
import base58
import codecs
import hashlib
from ecdsa import NIST256p, SigningKey
from server.utils import dict_utils
class Wallet:
    '''비트코인 전자지갑'''
    def __init__(self) -> None:
        self._private_key = SigningKey.generate(curve=NIST256p)
        self._public_key = self._private_key.get_verifying_key()
        self._blockchain_address = self.generate_blockchain_address()

    @property
    def blockchain_address(self) -> str:
        return self._blockchain_address

    @property
    def private_key(self) -> str:
        '''private key를 문자열로 변환'''
        return self._private_key.to_string().hex()

    @property
    def public_key(self) -> str:
        '''public key를 문자열로 변환'''
        return self._public_key.to_string().hex()

    def generate_blockchain_address(self) -> str:
        '''블록체인(지갑) 주소 생성'''
        # Step 1. __init__에서 이미 수행완료
        # Step 2. Public key에 SHA-256 수행
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        # Step 3. SHA-256 결과에 Ripemd160 수행
        ripemd160_bpk = hashlib.new('ripemd160')
        ripemd160_bpk.update(sha256_bpk_digest)
        ripemd160_bpk_digest = ripemd160_bpk.digest()
        ripemd160_bpk_digest_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
        # Step 4. Network byte 추가
        network_coin_public_key = b'00' + ripemd160_bpk_digest_hex
        network_coin_public_key_bytes = codecs.decode(
            network_coin_public_key, 'hex'
        )
        # Step 5. SHA-256 2회 수행
        sha256_bpk_digest = hashlib.sha256(network_coin_public_key_bytes).digest()
        sha256_2_bpk_digest = hashlib.sha256(sha256_bpk_digest).digest()
        sha256_hex = codecs.encode(sha256_2_bpk_digest, 'hex')
        # Step 6. Checksum 구하기
        checksum = sha256_hex[:8]
        # Step 7. Public key와 checksum 더하기
        addr_hex = (network_coin_public_key + checksum).decode('utf-8')
        # Step 8. 더한 키를 Base58로 인코딩
        blockchain_addr = base58.b58encode(addr_hex).decode('utf-8')

        return blockchain_addr

    @staticmethod
    def generate_signature(
        send_blockchain_addr: str,
        recv_blockchain_addr: str,
        send_private_key: str,
        amount: float
    ) -> str:
        '''거래에 필요한 signature 생성'''
        sha256 = hashlib.sha256()
        transaction = dict_utils.sorted_dict_by_key(
            {
                'send_blockchain_addr': send_blockchain_addr,
                'recv_blockchain_addr': recv_blockchain_addr,
                'amount': float(amount),
            }
        )
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()
        private_key = SigningKey.from_string(
            bytes().fromhex(send_private_key),
            curve=NIST256p
        )
        # Private Key로 서명하기
        private_key_sign = private_key.sign(message)
        signature = private_key_sign.hex()
        return signature

    def calculate_total_amount(self, blockchain_addr:str) -> float:
        '''blockchain_addr에 해당하는 계좌의 총액 구하기'''
        total_amount = 0.0
        for block in self.chain:
            # 체인으로 연결된 모든 블록을 검사
            for transaction in block['transactions']:
                # 개별 블록에 포함된 모든 거래 내역 검사
                value = float(transaction['amount'])
                if blockchain_addr == transaction['recv_blockchain_addr']:
                    # 계산할 주소와 돈 받은 주소가 동일하면 금액 추가
                    total_amount += value
                if blockchain_addr == transaction['send_blockchain_addr']:
                    # 계산할 주소와 송금한 주소가 동일하면 금액 빼기
                    total_amount -= value
        return total_amount


if __name__=='__main__':
    pass