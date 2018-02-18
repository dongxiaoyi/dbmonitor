import aiohttp
import asyncio
import aiomysql
import threading
import time
import os
import sys
from views.manage import controller, subintervel
from views.tools import start_loop, ExceptRestart
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from logs import logger

def event():
    """
    The program runs the entrance
    """
    loop = asyncio.new_event_loop()
    threads = threading.Thread(target=start_loop, args=(loop,))
    """
    .setDaemon(True) ensure that the main thread withdraws from the child thread and exits.
    """
    threads.setDaemon(True)
    threads.start()
    result = asyncio.run_coroutine_threadsafe(subintervel(loop), loop)
    asyncio.run_coroutine_threadsafe(controller(loop), loop)
    try:
        while result.result():
            """
            When the thread returns True, stop the current event loop, and then restart a cycle of events.
            """
            loop.stop()
            logger.warning('正在重启，等待... ...')
            time.sleep(5)
            event()
    except KeyboardInterrupt:
        """
        Guarantee the normal withdrawal of the event cycle.
        """
        logger.warning('-----------Event loop will exit-------------------')
        loop.stop()
        sys.exit(0)

if __name__ == '__main__':
    event()