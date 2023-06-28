'''
Author: Giseop Noh
Purpose: Implement CJU-coin P2P network by expanding git codes.
References
    1) https://github.com/macsnoeren/python-p2p-network
'''

from datetime import datetime
from pprint import pprint
import signal
import threading
import time
import config
import utils

from models import MiningNode
from nodeconnection import NodeConnection
from node import Node
from db_manager import DatabaseManager


class BlockChainNode(Node):
    def __init__(
        self,
        ip: str,
        port: int,
        id: str = None,
        hostname: str = None,
        callback: callable = None,
        max_connections: int = config.MAX_CONNECTIONS,
        public_ip = utils.get_external_ip(),
    ) -> None:

        super(BlockChainNode, self).__init__(ip, port, id, hostname, callback, max_connections)

        self.db_manager = DatabaseManager()
        self.db_manager.create_database()
        self.public_ip = public_ip
        self.init_self_node()
        self.send_keep_alive()
        self.check_is_active()
        self.register_public_ip_in_db()
        signal.signal(signalnum=signal.SIGINT, handler=self.signal_handler)


    def init_self_node(self) -> None:
        '''자신의 노드 정보 초기화'''
        node = self.db_manager.query_data(self.ip, self.port)
        if not node:
            new_node = self.build_new_node(self.ip, self.port)
            self.db_manager.insert_data(new_node)


    def register_public_ip_in_db(self) -> None:
        '''DB에 공인 ip 등록: 사설망을 사용할 경우 외부에서 접근할 ip 필요'''
        public_ip = utils.get_external_ip()
        node_exist = self.db_manager.query_data(public_ip, self.port)
        if not node_exist:
            node = self.build_new_node(public_ip, self.port)
            self.db_manager.insert_data(node)


    def signal_handler(self, signum, frame):
        print('\nCtrl+C 신호를 수신 -> 모든 노도와의 연결을 종료합니다.')
        # 모든 노드의 is_active를 False로 세팅
        nodes = self.db_manager.get_all_records()
        for node in nodes:
            node.is_active = False
            self.db_manager.insert_data(node)
        self.stop()
        exit(-1)


    def send_keep_alive(self, period: float = 1.0) -> None:
        '''현재 연결된 노드를 주기적으로 출력'''
        keep_alive_msg = {
            'type': 'keep_alive',
            'info':{
                    'ip': self.public_ip,
                    'port': self.port,
                    'timestamp': time.time(),
                }
        }
        # Sending keep_alive message to inbound nodes
        self.send_to_nodes(data=keep_alive_msg)
        threading.Timer(period, self.send_keep_alive).start()


    def check_is_active(self, time_interval: float = 3.0) -> None:
        '''time_interval에 따라 DB 저장된 모든 노드의 'is_active' 변경'''
        nodes = self.db_manager.get_all_records()
        for node in nodes:
            is_active = True if (time.time() - node.timestamp < config.IS_ACTIVE_INTERVAL) else False
            node.is_active = is_active
            self.db_manager.update_data(node)
        threading.Timer(time_interval, self.check_is_active).start()


    def build_new_node(self, ip: str, port: int) -> MiningNode:
        '''새로운 노드를 만들어서 리턴'''
        new_node = MiningNode()
        new_node.ip = ip
        new_node.port = port
        # is_active 자동 활성화 방지
        new_node.timestamp = time.time() - config.IS_ACTIVE_INTERVAL
        new_node.domain_name = self.hostname
        new_node.is_active = False
        return new_node


    def build_db_info_to_dict(self,) -> dict:
        '''데이터베이스에 있는 모든 정보를 사전 형태로 가공'''
        return {
            'type': 'blockchain_node',
            'info': self.db_manager.extract_all_data().get('info')
        }


    def outbound_node_connected(self, connected_node:Node):
        '''내가 다른 노드로 접속한 경우 경우'''
        print("\noutbound_node_connected: " + connected_node.id[:10])
        print(f'Me: {self.id[:10]} --> Outbound:{connected_node.id[:10]} ')
        print(f'Sending my data to outbound node...')
        my_data_in_db = self.build_db_info_to_dict()
        # 내 DB 정보를 접속한 node로 전송
        self.send_to_node(connected_node, data=my_data_in_db)


    def inbound_node_connected(self, connected_node):
        '''외부 노드가 나에게 접속한 경우'''
        print("\ninbound_node_connected: ")
        print(f'\tMe: {self.id[:10]} <-- Outbound: {connected_node.id[:10]}')
        my_data_in_db = self.build_db_info_to_dict()
        print(f'Sending my data to inbound nodes...')
        print(f'Me: {self.id[:10]} --> Inbound: {connected_node.id[:10]}')
        self.send_to_node(connected_node, my_data_in_db)


    def remove_node_from_node_list(self, connected_node: Node) -> None:
        if connected_node in self.nodes_inbound:
            self.nodes_inbound.remove(connected_node)
            print(f'inbound node removed: {connected_node.id[:10]}')
        if connected_node in self.nodes_outbound:
            self.nodes_outbound.remove(connected_node)
            print(f'Outbound node removed: {connected_node.id[:10]}')


    def inbound_node_disconnected(self, connected_node):
        '''외부에서 나한테 접속했던 노드가 끊긴 경우'''
        print("\ninbound_node_disconnected: " + connected_node.id[:10])
        node = self.db_manager.query_data(connected_node.ip, connected_node.port)
        self.set_is_active(node, False)
        self.remove_node_from_node_list(connected_node)


    def outbound_node_disconnected(self, connected_node):
        '''내가 외부로 접속했던 노드와 연결이 끊긴 경우'''
        print("outbound_node_disconnected: " + connected_node.id[:10])
        node = self.db_manager.query_data(connected_node.ip, connected_node.port)
        self.set_is_active(node, False)
        self.remove_node_from_node_list(connected_node)


    def set_is_active(self, mining_node: MiningNode, status: bool) -> None:
        mining_node.is_active = status
        mining_node.timestamp = time.time()
        self.db_manager.update_data(mining_node)


    def node_message(self, connected_node: Node, data: dict) -> None:
        '''현재 Node 객체가 외부 노드로부터 메시지를 받은 경우'''

        msg_type = data.get('type')

        # Processing 'blockchain_node': 해당노드 -> DB 업데이트
        if (isinstance(data, dict) and msg_type=='blockchain_node'):
            recv_items = data.get('info').values()
            for recv_item in recv_items:
                ip, port = recv_item.get('ip'), recv_item.get('port')
                if self.ip==ip and self.port==port:
                    continue # 자신은 업데이트 하지 않음
                new_node = MiningNode()
                new_node.ip = ip
                new_node.port = port
                new_node.domain_name = recv_item.get('hostname')
                new_node.timestamp = recv_item.get('timestamp')
                new_node.is_active = recv_item.get('is_active')
                self.db_manager.insert_data(new_node)

        # Processing 'keep_alive': Update timestamp & is_active
        if (isinstance(data, dict) and msg_type=='keep_alive'):
            recv_item = data.get('info')
            ip, port = recv_item.get('ip'), recv_item.get('port')
            node = self.db_manager.query_data(ip, port)
            if node:
                node.timestamp = time.time()
                node.is_active = True
                self.db_manager.update_data(node)


    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id[:10])


    def node_request_to_stop(self):
        print("node is requested to stop!")


    def create_new_connection(self, connection, id, ip, port):
        return NodeConnection(self, connection, id, ip, port)