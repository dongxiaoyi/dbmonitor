import aiomysql
import asyncio
from pymysql.err import ProgrammingError
import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from logs import logger
from setting import Config

agent_db = Config.AGENT_DB
server_db = Config.SERVER_DB


class AgentDBPool:
    """
    Generating a pool context manager with aiomysql like 'dbp=DBPool(loop)()'
    """
    def __init__(self, loop):
        self.__pool = aiomysql.create_pool(host = agent_db.host,
                                           user = agent_db.user,
                                           port = agent_db.port,
                                           password = agent_db.password,
                                           db = agent_db.db,
                                           loop = loop,
                                           )
    def __call__(self):
        return self.__pool


class ServerDBPool:
    """
    Generating a pool context manager with aiomysql like 'dbp=DBPool(loop)()'
    """
    def __init__(self, loop):
        self.__pool = aiomysql.create_pool(host = server_db.host,
                                           user = server_db.user,
                                           port = server_db.port,
                                           password = server_db.password,
                                           db = server_db.db,
                                           loop = loop,
                                           )
    def __call__(self):
        return self.__pool

def start_loop(loop):
    """
    Open the event loop.
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()