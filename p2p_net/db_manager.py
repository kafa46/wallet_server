import logging
import time
import config

from datetime import datetime
from pprint import pprint
from typing import List, Union
from sqlalchemy import (
    create_engine,
    select
)
from sqlalchemy.orm import (
    Session,
)

# from models import Base, MiningNode
# from p2p_net.models import Base, MiningNode
from models import Base, MiningNode

logger = logging.getLogger(__name__)


class DatabaseManager:
    '''Manage P2P Database'''
    def __init__(self,) -> None:
        self.base = Base()
        self.engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)
        # self.session = Session(self.engine)

    def create_database(self,) -> bool:
        '''create empty schema in our database
            Note: https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.MetaData.create_all
            Create all tables stored in this metadata.
            Conditional by default, will not attempt to recreate
            tables already present in the target database.'''
        self.base.metadata.create_all(self.engine)

    def insert_data(self, data: MiningNode) -> bool:
        '''insert data to DB'''
        # ip:port 동일한 node가 있는지 확인
        node =  self.query_data(data.ip, data.port)
        # 만약 ip:port 정보가 있다면 나머지 정보만 업데이트
        if node:
            self.update_data(data)
            return True
        # 만약 ip:port 정보가 없다면 새롭게 추가
        with Session(self.engine) as session:
            try:
                session.add(data)
                session.commit()
                return True
            except Exception as e:
                print(f'Error: {e}')
                return False

    def update_data(self, data: MiningNode) -> bool:
        '''update database using data'''
        node =  self.query_data(data.ip, data.port)
        if not node:
            return False
        with Session(self.engine) as session:
            if data.timestamp:
                node.timestamp = data.timestamp
            node.is_active = data.is_active
            session.add(node)
            session.commit()
        return True


    def delete_data(self, ip: str, port: int) -> bool:
        '''delete data from database'''
        node =  self.query_data(ip, port)
        if not node:
            print('cannot delete for non-existing data')
            return False
        with Session(self.engine) as session:
            # node_for_delete = node[0]
            # obj_for_delete = session.get(MiningNode, node_for_delete.id)
            session.delete(node)
            # session.delete(obj_for_delete)
            session.commit()
        return True


    def query_data(self, ip: str, port: int) -> MiningNode:
        '''query data with ip:port, and return MiningNode object'''
        with Session(self.engine) as session:
            stmt = select(MiningNode).where(
                MiningNode.ip==ip).where(MiningNode.port==port)
            result = session.scalar(stmt)
        if not result:
            return False
        return result


    def get_all_records(self) -> List[MiningNode]:
        '''데이터베이스 모든 레코드를 리턴'''
        with Session(self.engine) as session:
            stmt = select(MiningNode).order_by(MiningNode.timestamp.desc())
            return [node for node in session.scalars(stmt)]


    def extract_all_data(self,) -> dict:
        '''DB에 있는 모든 데이터 추출하여 dict로 가공하여 리턴'''
        with Session(self.engine) as session:
            stmt = select(MiningNode).order_by(MiningNode.timestamp.desc())
            info = {
                idx: self.convert_item_to_dict(item) for idx, item in enumerate(session.scalars(stmt))
            }
            result = {
                'type': 'blockchain_node',
                'info': info
            }
        return result

    def get_active_node(self,) -> MiningNode:
        '''DB에 있는 노드 중에서 현재 연결상태인 노드를 리턴'''
        with Session(self.engine) as session:
            stmt = select(MiningNode).where(MiningNode.is_active==True).order_by(MiningNode.timestamp.desc())
            return session.scalar(stmt)


    def convert_item_to_dict(self, item:MiningNode) -> dict:
        '''데이터베이스 아이템을 dict로 변환'''
        return {
            'hostname': item.domain_name,
            'ip': item.ip,
            'port': item.port,
            'timestamp': item.timestamp,
            'is_active': item.is_active,
        }


    def commit_node_object(self, item: MiningNode) -> None:
        with Session(self.engine) as session:
            session.add(item)
            session.commit()


if __name__=='__main__':
    manager = DatabaseManager()
    manager.create_database()

    data = MiningNode(
        ip='127.0.0.1',
        port=22901,
        domain_name='Deep Learning',
        timestamp=time.time(),
        last_access=datetime.now(),
        initial_access=datetime.now(),
        is_active=True,
    )
    manager.insert_data(data)

    data = manager.extract_all_data()
    print(f'\nmanager.extract_all_data():')
    pprint(data)

    # data = MiningNode(
    #     ip='203.252.240.43',
    #     port=22901,
    #     domain_name='Deep Test',
    #     timestamp=time.time(),
    #     last_access=datetime.now(),
    #     initial_access=datetime.now(),
    #     is_active=True,
    # )
    # manager.insert_data(data)

    # res = manager.query_data('203.252.240.43', 22901)
    # if res:
    #     for item in res:
    #         print(item.id)

    # data = MiningNode(
    #     ip='203.252.240.43',
    #     port=22901,
    #     domain_name='Deep insert',
    #     timestamp=time.time(),
    #     last_access=datetime.now(),
    #     initial_access=datetime.now(),
    #     is_active=True,
    # )
    # manager.insert_data(data)

    # manager.delete_data('203.252.240.43', 22901)