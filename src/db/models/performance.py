# -*- coding:utf-8 -*-
'''
MySQL performance metrics related data model
'''

from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

from .Models import Base


class QueryThroughput(Base):
    '''
    performance metrics: Query throughput
    '''
    __tablename__ = 'querythrougput'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    questions = Column('questions', Integer, nullable=False, default=0)
    com_select = Column('com_select', Integer, nullable=False, default=0)
    writes = Column('writes', Integer, nullable=False, default=0)
    create_time = Column('create_time', DateTime, nullable=True, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class QueryPerformance(Base):
    '''
    performance metrics: Query perfomance
    '''
    __tablename__ = 'queryperformance'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    table = Column('table', String(200), nullable=False, default='')
    avgmicrosec = Column('avgmicrosec', Integer, nullable=False, default=0)
    err_count = Column('err_count', Integer, nullable=False, default=0)
    create_time = Column('create_time', DateTime, nullable=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class Connections(Base):
    '''
    performance metrics: Connections
    '''
    __tablename__ = 'connections'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    max_connections = Column('max_connections', Integer, nullable=False, default=0)
    threads_connected = Column('threads_connected', Integer, nullable=False, default=0)
    threads_running = Column('threads_running', Integer, nullable=False, default=0)
    connection_errors_internal = Column('connection_errors_internal', Integer, nullable=False, default=0)
    aborted_connects = Column('aborted_connects', Integer, nullable=False, default=0)
    connection_errors_max_connections = Column('connection_errors_max_connections', Integer, nullable=False, default=0)
    create_time = Column('create_time', DateTime, nullable=False, default=0)


class InnodbBufferPool(Base):
    '''
    performance metrics: Innodb buffer pool
    '''
    __tablename__ = 'innodbbufferpool'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    innodb_buffer_pool_pages_total = Column('innodb_buffer_pool_pages_total', Integer, nullable=False, default=0)
    innodb_buffer_pool_rate = Column('innodb_buffer_pool_rate', Integer, nullable=False, default=0)
    innodb_buffer_pool_read_requests = Column('innodb_buffer_pool_read_requests', Integer, nullable=False, default=0)
    innodb_buffer_pool_reads = Column('innodb_buffer_pool_reads', Integer, nullable=False, default=0)
    innodb_page_size = Column('innodb_page_size', Integer, nullable=False, default=0)
    create_time = Column('create_time', DateTime, nullable=False, default=0)