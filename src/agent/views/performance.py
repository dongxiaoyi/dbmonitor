import asyncio
import aiomysql
from pymysql.err import ProgrammingError
from collections import namedtuple
import arrow
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from logs import logger
from setting import Config
from utils import Singleton

hostname = Config.HOSTNAME

"""SQL for get performance index"""

'''Query throughput related index SQL statement'''
# 已执行语句（由客户端发出）计数
QUESTIONS = 'SHOW GLOBAL STATUS LIKE "Questions";'
# SELECT 语句计数
COM_SELECT = 'SHOW GLOBAL STATUS LIKE "Com_select";'
# INSERT 语句计数
COM_INSERT = 'SHOW GLOBAL STATUS LIKE "Com_insert";'
# UPDATE 语句计数
COM_UPDATE = 'SHOW GLOBAL STATUS LIKE "Com_update";'
# DELETE 语句计数
COM_DELETE = 'SHOW GLOBAL STATUS LIKE "Com_delete";'


'''query performance index'''

"""Extract the average running time in microseconds by mode and calculate the total number of statements that are wrong"""
PERFORMANCE = 'SELECT *, NOW() AS create_time \
               FROM \
                    (SELECT schema_name, \
                            SUM(count_star) count, \
                            ROUND(   (SUM(sum_timer_wait) / SUM(count_star)) / 1000000) AS avg_microsec \
                     FROM performance_schema.events_statements_summary_by_digest \
                     WHERE schema_name IS NOT NULL \
                     GROUP BY schema_name) \
                AS a \
                JOIN \
                    (SELECT schema_name, \
                            SUM(sum_errors) err_count   \
                     FROM performance_schema.events_statements_summary_by_digest    \
                     WHERE schema_name IS NOT NULL    GROUP BY schema_name) \
                AS b \
                USING (schema_name);'

'''连接性能指标SQL语句'''
# 显示最大连接数限制
MAX_CONN = "SHOW VARIABLES LIKE 'max_connections';"
# 当前开放的连接
THREADS_CONNCTED = "SHOW GLOBAL STATUS like 'Threads_connected';"
# 当前运行的连接
THREADS_RUNNING = "SHOW GLOBAL STATUS like 'Threads_running';"
# 由服务器错误导致的失败连接数
CONNECTION_ERRORS_INTERNAL = "SHOW GLOBAL STATUS like 'Connection_errors_internal';"
# 尝试与服务器进行连接结果失败的次数
ABORTED_CONNECTS = "SHOW GLOBAL STATUS like 'Aborted_connects';"
# 由 max_connections 限制导致的失败连接数
CONNECTION_ERRORS_MAX_CONNECTIONS = "SHOW GLOBAL STATUS like 'Connection_errors_max_connections';"
'''缓冲池连接使用率相关指标SQL语句'''
# 获取缓冲池大小
INNODB_BUFFER_POOL_SIZE = 'SHOW VARIABLES LIKE "innodb_buffer_pool_size";'
# 计算缓冲池利用率相关SELECT schema_name, SUM(count_star) count, ROUND(   (SUM(sum_timer_wait) / SUM(count_star)) / 1000000) AS avg_microsec FROM performance_schema.events_statements_summary_by_digest WHERE schema_name IS NOT NULL GROUP BY schema_name;
# 缓冲池总页数
INNODB_BUFFER_POOL_PAGES_TOTAL = 'SHOW GLOBAL STATUS LIKE "Innodb_buffer_pool_pages_total";'
# 缓冲池空闲页数
INNODB_BUFFER_POOL_PAGES_FREE = 'SHOW GLOBAL STATUS LIKE "Innodb_buffer_pool_pages_free";'
# 向缓冲池发送的请求
INNODB_BUFFER_POOL_READ_REQUESTS = 'SHOW GLOBAL STATUS LIKE "Innodb_buffer_pool_read_requests";'
# 缓冲池无法满足的请求
INNODB_BUFFER_POOL_READS = 'SHOW GLOBAL STATUS LIKE "Innodb_buffer_pool_reads";'
# INNODB页面大小
INNODB_PAGE_SIZE = 'SHOW VARIABLES LIKE "innodb_page_size";'


class PerformanceInfo:
    """
    Read the client database performance information and write to the server database.
    :param agent_pool: MySQL context manager Object.
    :param server_pool: MySQL context manager Object.
    """
    def __init__(self, agent_pool, server_pool):
        self.__agent_pool = agent_pool
        self.__server_pool = server_pool

    async def dbinfo(self):
        pool = await self.__agent_pool
        now = arrow.now()
        create_time = now.format('YYYY-MM-DD HH:mm:ss')
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(QUESTIONS)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % QUESTIONS))
                    os._exit(0)
                else:
                    (_, questions) = await cur.fetchone()
                try:
                    await cur.execute(COM_SELECT)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % COM_SELECT))
                else:    
                    (_, com_select) = await cur.fetchone()
                try:
                    await cur.execute(COM_INSERT)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % COM_INSERT))
                else:    
                    (_, com_insert) = await cur.fetchone()
                try:
                    await cur.execute(COM_UPDATE)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % COM_UPDATE))
                else:    
                    (_, com_update) = await cur.fetchone()
                try:
                    await cur.execute(COM_DELETE)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % COM_DELETE))
                else:    
                    (_, com_delete) = await cur.fetchone()
                writes = (int(com_insert) + int(com_update) + int(com_delete))
                await cur.close()
            conn.close()

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(PERFORMANCE)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % PERFORMANCE))
                    os._exit(0)
                else:
                    performance = []
                    for db, count, avgmicrosec, err_count, create_time in await cur.fetchall():
                        performance.append((db, count, avgmicrosec, err_count))
                await cur.close()
            conn.close()

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(MAX_CONN)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % MAX_CONN))
                    os._exit(0)
                else:
                    (_, max_conn) = await cur.fetchone()
                try:
                    await cur.execute(THREADS_CONNCTED)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % THREADS_CONNCTED))
                    os._exit(0)
                else:
                    (_, threads_connected) = await cur.fetchone()
                
                try:
                    await cur.execute(THREADS_RUNNING)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % THREADS_RUNNING))
                    os._exit(0)
                else:
                    (_, threads_running) = await cur.fetchone()
                
                try:
                    await cur.execute(ABORTED_CONNECTS)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % ABORTED_CONNECTS))
                    os._exit(0)
                else:
                    (_, aborted_connects) = await cur.fetchone()
                
                try:
                    await cur.execute(CONNECTION_ERRORS_INTERNAL)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % CONNECTION_ERRORS_INTERNAL))
                    os._exit(0)
                else:
                    (_, connection_errors_internal) = await cur.fetchone()
                
                try:
                    await cur.execute(CONNECTION_ERRORS_MAX_CONNECTIONS)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % CONNECTION_ERRORS_MAX_CONNECTIONS))
                    os._exit(0)
                else:
                    (_, connection_errors_max_connections) = await cur.fetchone()

                await cur.close()
            conn.close()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(INNODB_BUFFER_POOL_SIZE)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % INNODB_BUFFER_POOL_SIZE))
                    os._exit(0)
                else:
                    (_, innodb_buffer_pool_size) = await cur.fetchone()

                try:
                    await cur.execute(INNODB_BUFFER_POOL_PAGES_TOTAL)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % INNODB_BUFFER_POOL_PAGES_TOTAL))
                    os._exit(0)
                else:
                    (_, innodb_buffer_pool_pages_total) = await cur.fetchone()
                
                try:
                    await cur.execute(INNODB_BUFFER_POOL_PAGES_FREE)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % INNODB_BUFFER_POOL_PAGES_FREE))
                    os._exit(0)
                else:
                    (_, innodb_buffer_pool_pages_free) = await cur.fetchone()
                
                try:
                    await cur.execute(INNODB_BUFFER_POOL_READ_REQUESTS)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % INNODB_BUFFER_POOL_READ_REQUESTS))
                    os._exit(0)
                else:
                    (_, innodb_buffer_pool_read_requests) = await cur.fetchone()

                try:
                    await cur.execute(INNODB_BUFFER_POOL_READS)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % INNODB_BUFFER_POOL_READS))
                    os._exit(0)
                else:
                    (_, innodb_buffer_pool_reads) = await cur.fetchone()
                
                try:
                    await cur.execute(INNODB_PAGE_SIZE)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % INNODB_PAGE_SIZE))
                    os._exit(0)
                else:
                    (_, innodb_page_size) = await cur.fetchone()
                await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()
        return {'create_time': create_time,
                'Throughput': (questions, com_select, writes),
                'Performance': performance,
                'Connections': (max_conn, threads_connected, threads_running, aborted_connects,
                                connection_errors_internal, connection_errors_max_connections),
                'Innodb': (innodb_buffer_pool_size, innodb_buffer_pool_pages_total,
                           innodb_buffer_pool_pages_free, innodb_buffer_pool_read_requests,
                           innodb_buffer_pool_reads, innodb_page_size)
                }

    async def save_sql(self):
        try:
            data = await self.dbinfo()
        except Exception as e:
            logger.error("Get agent data error", exc_info=True)
            os._exit(0)
        else:
            
            server_dbpool = await self.__server_pool
            create_time = data['create_time']
            performance = data['Performance']
            throughput = data['Throughput']
            connections = data['Connections']
            innodb = data['Innodb']
            async with server_dbpool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        questions, com_select, writes = throughput
                        save_throughput_sql = 'INSERT INTO Throughput(hostname, questions, com_select, writes, create_time) VALUES("%s", %d, %d, %d, "%s");'% (hostname, int(questions), int(com_select), int(writes), create_time)
                        await cur.execute(save_throughput_sql)
                    except ProgrammingError as e:
                        logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % save_throughput_sql))
                        os._exit(0)
                    else:
                        logger.info('(Success: %s)' % save_throughput_sql)
                    
                    for raw in performance:
                        try:
                            db, count, avgmicrosec, err_count = raw
                            save_queryperformance_sql = 'INSERT INTO Performance(hostname, db_name, avgmicrosec, err_count, create_time) VALUES("%s", "%s", %d, %d, "%s");' % (hostname, str(db), int(avgmicrosec), int(err_count), create_time)
                            await cur.execute(save_queryperformance_sql)
                        except ProgrammingError as e:
                            logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % save_queryperformance_sql))
                            os._exit(0)
                        else:
                            logger.info('(Success: %s)' % save_queryperformance_sql)
                    
                    try:
                        max_conn, threads_connected, threads_running, aborted_connects, connection_errors_internal, connection_errors_max_connections = connections
                        save_connections_sql = 'INSERT INTO Connections(hostname, max_connections, threads_connected, threads_running, aborted_connects, connection_errors_internal, connection_errors_max_connections, create_time) VALUES("%s", %d, %d, %d, %d, %d, %d,"%s");' % (hostname, int(max_conn),int(threads_connected),int(threads_running),int(aborted_connects),int(connection_errors_internal),int(connection_errors_max_connections), create_time)
                        await cur.execute(save_connections_sql)
                    except ProgrammingError as e:
                        logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % save_connections_sql))
                        os._exit(0)
                    else:
                        logger.info('(Success: %s)' % save_connections_sql)
                    
                    try:
                        innodb_buffer_pool_size, innodb_buffer_pool_pages_total, innodb_buffer_pool_pages_free, innodb_buffer_pool_read_requests, innodb_buffer_pool_reads, innodb_page_size = innodb
                        save_innodbbufferpool_sql = 'INSERT INTO Innodb(hostname, innodb_buffer_pool_pages_total, innodb_buffer_pool_read_requests, innodb_buffer_pool_reads, innodb_buffer_pool_rate, innodb_page_size, create_time) VALUES("%s", %d, %d,%d,%d, %d, "%s");' % (hostname, int(innodb_buffer_pool_pages_total),int(innodb_buffer_pool_read_requests),int(innodb_buffer_pool_reads), ((int(innodb_buffer_pool_pages_total) - int(innodb_buffer_pool_pages_free)) / int(innodb_buffer_pool_pages_total)), int(innodb_page_size), create_time)
                        await cur.execute(save_innodbbufferpool_sql)
                    except ProgrammingError as e:
                        logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % save_connections_sql))
                        os._exit(0)
                    else:
                        logger.info('(Success: %s)' % save_connections_sql)

                    await conn.commit()
                    await cur.close()
            server_dbpool.close()
            await server_dbpool.wait_closed()

    async def agent_dbs(self):
        pool = await self.__agent_pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    dbs_sql = "SHOW DATABASES;"
                    await cur.execute(dbs_sql)
                except Exception as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % dbs_sql), exc_info=True)
                    os._exit(0)
                else:
                    dbs = await cur.fetchall()
                await cur.close()
        pool.close()
        await pool.wait_closed()
        return [list(db)[0] for db in dbs]

    async def register(self):
        dbs = str(await self.agent_dbs())
        server_dbpool = await self.__server_pool
        async with server_dbpool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    check_register_sql = "SELECT hostname FROM Agent WHERE hostname='%s';" % hostname
                    await cur.execute(check_register_sql)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % check_register_sql))
                    os._exit(0)
                else:
                    try:
                        (host, ) = await cur.fetchall()
                    except Exception as e:
                        try:
                            register_sql = 'INSERT INTO Agent(hostname, status, dbs) VALUES("%s", "running", "%s");' % (hostname, dbs)
                            await cur.execute(register_sql)
                        except ProgrammingError as e:
                            logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % register_sql), exc_info=True)
                            os._exit(0)
                        else:
                            logger.info('(Regist agent successful: %s)' % hostname)
                            await conn.commit()
                            await cur.close()
                            conn.close()
                            server_dbpool.close()
                            await server_dbpool.wait_closed()
                    else:
                        if not host:
                            try:
                                register_sql = 'INSERT INTO Agent(hostname, status) VALUES("%s", "running", "%s");' % (hostname, dbs)
                                await cur.execute(register_sql)
                            except ProgrammingError as e:
                                logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % register_sql))
                                os._exit(0)
                            else:
                                logger.info('(Regist agent successful: %s)' % hostname)
                                await conn.commit()
                                await cur.close()
                                conn.close()
                                server_dbpool.close()
                                await server_dbpool.wait_closed()
                        else:
                            logger.info('(%s is registed)' % hostname)
                try:
                    interverl_sql = "SELECT intervel FROM Agent WHERE hostname='%s';" % hostname
                    await cur.execute(interverl_sql)
                except ProgrammingError as e:
                    logger.error("(%s)" % ProgrammingError('SQL syntax error: %s' % interverl_sql))
                    os._exit(0)
                else:
                    (intervel, ) = await cur.fetchone()
                    print('时间啊', intervel)
                await cur.close()
            conn.close()
        server_dbpool.close()
        await server_dbpool.wait_closed()
        return intervel