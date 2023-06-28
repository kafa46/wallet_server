'''블록체인 노드 정보를 제공하기 위한 DB 관리자'''

from datetime import datetime
from pprint import pprint
from typing import List, Union
from sqlalchemy import (
    create_engine,
    select
)
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
)
from p2p_net.models import MiningNode
import config

class P2PManager:
    '''블록체인 P2P 네트워크 지원 관리자'''

    def __init__(self,) -> None:
        self.base = DeclarativeBase()
        self.engine = create_engine(config.P2P_DATABASE_URI, echo=False)

    def get_one_active_node(self,) -> MiningNode:
        '''DB에 있는 노드 중에서 현재 연결상태인 노드를 리턴'''
        with Session(self.engine) as session:
            stmt = select(MiningNode).where(MiningNode.is_active==True).order_by(MiningNode.timestamp.desc())
            return session.scalar(stmt)