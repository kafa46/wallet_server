import os

BASE_DIR = os.getcwd()
# BASE_DIR = '/home/kafa46/workspace/flask_app/path_to_project'

print(BASE_DIR)

# 'sqlite:///' -> 사용할 DB는 SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    os.path.join(BASE_DIR, 'p2p.db')
)

print(SQLALCHEMY_DATABASE_URI)

# 비밀번호 최소 길이
MIN_LENGTH_OF_PASSWD = 7

# 블록체인 네트워크 P2P node 통신에 사용할 포트
P2P_PORT = 22901

# Seed Server
SEED_SERVER_IP = '203.252.240.43'
SEED_SERVER_PORT = 22900

# 최대 연결 노드의 개수
MAX_CONNECTIONS = 10

# 자신의 공인 아이피를 확인하기 위해 이용한 서비스 프로바이더
# Other possible service-providers
#   - https://ident.me
#   - https://api.ipify.org
#   - http://myip.dnsomatic.com/
IP_CHECK_SERVICE_PROVIDER = 'https://checkip.amazonaws.com'

# 블록체인 노드에서 is_active 업데이트 주기
IS_ACTIVE_INTERVAL = 3.0