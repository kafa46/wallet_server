import platform
import sys
import argparse
import time
import utils
import config
from db_manager import DatabaseManager
from p2p_network import BlockChainNode

def parser():
    parser = argparse.ArgumentParser(description='Blockchain P2P Network')
    parser.add_argument(
        '--port', '-p',
        default=config.P2P_PORT,
        help='port number for this P2P node'
    )
    parser.add_argument(
        '--seed-ip', '-si',
        default=config.SEED_SERVER_IP,
        help='The IP address of blockchain seed node',
    )
    parser.add_argument(
        '--seed-port', '-sp',
        default=config.SEED_SERVER_IP,
        help='The port number of blockchain seed server',
    )
    parser.add_argument('--repeat', '-r', action='store_true')
    return parser.parse_args()


def run():
    args = parser()
    # 운영체제별 실행방법 설정
    # Linux: 'Linux', Mac: 'Darwin', Windows: 'Windows'
    os_type = platform.system()
    # if os_type == 'Windows':
    #     # To do
    #     pass
    # if os_type == 'Darwin':
    #     # To do
    #     pass
    # elif os_type == 'Linux':
    #     # To do
    #     pass
    # else:
    #     print('지원하지 않는 운영체제 입니다.')
    #     return False

    if not (os_type=='Windows' or os_type == 'Linux'):
        print('지원하는 운영체지(Windows 또는 Linux)가 아닙니다.')
        print('프로그램을 종료합니다.\n')
        exit(-1)

    # 게이트웨이(또는 공유기) 확인하기 위한 ip 확인
    ip_internal = utils.get_internal_ip()
    ip_external = utils.get_external_ip()

    if ip_internal == ip_external:
        '''현재 컴퓨터에 공인 IP가 할당된 경우'''
        ip = ip_external
    else:
        '''공유기 또는 사설망을 사용하는 경우 -> 포트포워딩 설정'''
        print(f'사설망을 사용하는 것 같습니다.')
        print(f'공유기 (또는 게이트웨이에서) 포트를 개방해야 합니다.')
        print(f'씨쥬코인 마이닝 포트 {config.P2P_PORT} 입니다.')
        # 공유기 외부(공인) ip로 객체를 생성하면
        # socket bind 에러 발생
        #   -> OSError: [WinError 10049] 요청한 주소는 해당 컨텍스트에서 유효하지 않습니다
        # 객체 생성시 사설 ip로 초기화 하고 outbound 연결 요청 시 공인 ip 전송하도록 코딩
        # ip = ip_external
        ip = ip_internal

    port = int(args.port)
    hostname = utils.get_current_hostname()
    node = BlockChainNode(ip, port, hostname=hostname)
    node.start()

    print('씨쥬코인 네트워크 노드와 연결을 시도합니다.')
    db_manager = DatabaseManager()
    node_dic = db_manager.extract_all_data()
    connection_count = 0
    num_nodes_in_db = len(node_dic.get('info'))
    print(f'\n{num_nodes_in_db}개 노드와 접속을 시도합니다.')
    print(node_dic.get('info'))

    # # Seed 노드와 최초 연결 시도
    # seed_node_connect_success = node.connect_with_node(config.SEED_SERVER_IP, config.SEED_SERVER_PORT)
    # if seed_node_connect_success:
    #     print('Seed 블록체인 노드 연결에 성공했습니다.')

    for item in node_dic.get('info').values():
        # 자신과는 연결하지 않음
        if (
            (ip==item.get("ip") and port==item.get("port"))
            or
            (ip==utils.get_external_ip() and port==item.get("port"))
        ):
            print('자기 자신과는 연결하지 않습니다.')
            print(f'ip_ext, self.port: {ip_external}:{port} --> skipping')
            print(f'ip_int, self.port: {ip_internal}:{port} --> skipping')
            continue

        # 자신과의 연결이 아니라면 메시지 출력하고 연결 시도
        print(
            f'연결시도: Me {ip}:{port} ---> Target: {item.get("ip")}:{item.get("port")}',
            end='\t'
        )
        connection_success = node.connect_with_node(item.get('ip'), item.get('port'))
        if connection_success:
            print('성공!')
            connection_count += 1
            if connection_count >= config.MAX_CONNECTIONS:
                break
        else:
            print('실패 ㅠㅠ')
    print(f'{connection_count}개 노드와 접속하였습니다.\n')


if __name__=='__main__':
    run()