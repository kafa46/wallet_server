from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    Boolean
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    '''simple subclass for basic use'''
    pass


class MiningNode(Base):
    __tablename__='mining_node'

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(String(30))
    port: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[float] = mapped_column(Float)
    domain_name: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self):
        return f'MiningNode({self.ip_addr}:{self.port})'