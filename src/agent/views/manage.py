import asyncio
import arrow
import re
import aioredis
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from logs import logger
from setting import Config

from .tools import ServerDBPool, AgentDBPool
from .performance import PerformanceInfo
from .tools import ExceptRestart
DEFAULT_SETTING_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'setting/config_pro.yml')
# Client's IP/hostname
hostname = Config.HOSTNAME

async def controller(loop):
    """
    Loop query MySQL performance index.
    """
    agent_dbpool = AgentDBPool(loop)()
    server_dbpool = ServerDBPool(loop)()
    performance = PerformanceInfo(agent_pool=agent_dbpool, server_pool=server_dbpool)
    try:
        """
        Check whether the client is registered or not.
        returns: performance query interval.
        """
        intervel = await performance.register()
    except Exception as e:
        logger.error('register agent fail!', exc_info=True)
    else:
        print('-------start monitor-------')
        while True:
            try:
                start = arrow.now()
                # This step is to generate a new pool, and an aiomysql pool context manager can only generate a pool and discarded it.
                agent_dbpool = AgentDBPool(loop)()
                server_dbpool = ServerDBPool(loop)()
                performance = PerformanceInfo(agent_pool=agent_dbpool, server_pool=server_dbpool)
                await performance.save_sql()
            except Exception as e:
                logger.error(('save db information error!'), exc_info=True)
                os._exit(0)
            else:
                end = arrow.now()
                """
                Filtration performance loss time, guarantee the accuracy of query interval.
                """
                intervel = intervel - int(((end - start).total_seconds()))
                logger.info('(Please wait: %s s)'% intervel)
                """
                Cycle query once per Intervel time.
                """
                await asyncio.sleep(intervel)
                
# Redis Publish/subscribe monitor channel.
pubsub_channel = 'intervel:hostname:intervel'

async def subintervel(loop):
    logger.info('-------start check intervel-------')
    sub = await aioredis.create_pool(('127.0.0.1', 6379), db=0, loop=loop)
    async with sub.get() as conn:
        res = await conn.subscribe(pubsub_channel)
        ress = res[0]
        while (await ress.wait_message()):
            msg = await ress.get_json()
            if msg.split(':')[0] == hostname:
                intervel = int(msg.split(':')[1])
                logger.info('监控间隔发生改变：%s' % intervel)
                logger.info('-------客户端即将重启-------')
                return True
            
