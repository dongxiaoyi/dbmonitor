#-*- coding: utf-8 -*-
import numpy as np
import pandas as  pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter 
import seaborn as sns
from io import BytesIO
import base64
from sanic import Blueprint
from sanic.response import json
import arrow as aw
import os
import sys

performance_v1 = Blueprint('performance', url_prefix='/v1/performance')
performance_blueprint = performance_v1


async def performance_dynamic_img(data):
    """
    Generating query performance index pictures.
    """
    sns.set(color_codes=True, palette='deep', font_scale=.8)
    fig = plt.figure(figsize=(15, 12))
    ax1 = fig.add_subplot(2,1,1)
    plt.plot(data['create_time'], data['avgmicrosec'], color='y', linestyle='--', label='avgmicrosec')
    plt.legend(loc="upper left")
    plt.title(u'Average query latency')
    ax2 = fig.add_subplot(2,1,2)
    plt.plot(data['create_time'], data['err_count'], color='b', label='err_count')
    plt.legend(loc='upper left')
    plt.title(u'Number of error SQL statements')
    buffer = BytesIO()
    plt.savefig(buffer, dpi=110)  
    performance_data = buffer.getvalue()
    performance_data_b = base64.b64encode(performance_data)
    performance_data_d = performance_data_b.decode()
    imgd = "data:image/png;base64," + performance_data_d
    plt.close()
    buffer.close()
    return imgd

@performance_blueprint.route('/', methods=['GET', 'PATCH', 'OPTIONS'])
async def performance(request):
    """
    Query performance API interface.
    """
    if request.method == 'GET':
        try:
            (agent, ) = await request.app.mysql.query('SELECT hostname FROM Agent limit 1;')
            hostname= agent[0]
        except Exception as e:
            logger.error('Query agent hostname error', exc_info=True)
            os._exit(0)
        else:
            try:
                (db_info,) = await request.app.mysql.query('SELECT db_name FROM Performance WHERE hostname="%s" LIMIT 1;' % hostname)
            except Exception as e:
                logger.error('Query agent db name error', exc_info=True)
                os._exit(0)
            else:
                db_name = db_info[0]
        today = aw.now()
        yesterday = today.replace(days=-1)
        yesterday = yesterday.format('YYYY-MM-DD HH:mm:ss')
        default_sql = "SELECT avgmicrosec, err_count, create_time FROM Performance WHERE hostname='%s' AND db_name='%s' AND create_time >'%s';" % (hostname, db_name, yesterday)
        try:
            val = await request.app.mysql.query(default_sql)
        except Exception as e:
            logger.error('Query agent performance information error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['avgmicrosec', 'err_count', 'create_time'])
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        imgd = await performance_dynamic_img(data)
        return json({'performance': imgd, 'hostname': [hostname,], 'db_name': [db_name,], 'intervel': intervel})
    
    elif request.method in ['POST', 'PUT', 'PATCH']:
        hostname_db = request.json
        host = hostname_db['hostname_db'][0]
        db = hostname_db['hostname_db'][1]
        times = hostname_db['times']
        time_start = aw.get(times[0]).format('YYYY-MM-DD HH:mm:ss')
        time_end = aw.get(times[1]).format('YYYY-MM-DD HH:mm:ss')
        query_sql = "SELECT avgmicrosec, err_count, create_time FROM Performance WHERE hostname='%s' AND db_name='%s' AND create_time >'%s' AND create_time <'%s';" % (host, db, time_start, time_end)
        try:
            val = await request.app.mysql.query(query_sql)
        except Exception as e:
            logger.error('Query agent performance information error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['avgmicrosec', 'err_count', 'create_time'])
        imgd = await performance_dynamic_img(data)
        return json({'performance': imgd, 'hostname': [host,], 'db_name': [db,]})
    

@performance_blueprint.route('/dbs', methods=['GET', 'POST', 'PUT', 'PATCH'])
async def get_allinfo(request):
    """
    Access to the interface of the database/（hostname/IP）
    """
    if request.method == 'GET':
        dbs_info = await request.app.mysql.query('SELECT hostname, dbs FROM Agent;')
        dbs = [{'value': db[0], 'label': db[0], 'children': [{'value': dbname, 'label': dbname} for dbname in eval(db[1])]} for db in dbs_info]
        return json(dbs)

"""Redis Publish/subscribe monitor channel."""
pubsub_channel = 'intervel:hostname:intervel'

@performance_blueprint.route('/intervel', methods=['PATCH', 'OPTIONS'])
async def set_intervel(request):
    """
    Setting the client query interval.
    """
    if request.method =='PATCH':
        data = request.json
        hostname = data['hostname']
        intervel = data['intervel']
        if isinstance(intervel, list):
            intervel = intervel[0][0]
        update_intervel_sql = "UPDATE Agent SET intervel=%d WHERE hostname='%s';" % (int(intervel), hostname)
        try:
            await request.app.mysql.query(update_intervel_sql)
        except Exception as e:
            logger.error('Alter agent intervel failed!', exc_info=True)
            os._exit(0)
        with await request.app.redis as r:
            await r.publish_json(pubsub_channel, "%s:%d" % (hostname, int(intervel)))
        return json({'intervel_warn': 'success'})


async def throughput_dynamic_img(data):
    """
    Generating throughput index pictures.
    """
    sns.set(color_codes=True, palette='deep', font_scale=.8)
    plt.bar(data['create_time'], data['questions'], color='y', linestyle='--', label='questions')
    plt.bar(data['create_time'], data['com_select'], color='r', linestyle='--', label='com_select')
    plt.bar(data['create_time'], data['writes'], color='b', linestyle='--', label='writes')
    plt.legend(loc="upper left")
    plt.title(u'Mysql questions')
    plt.legend(loc='upper left')
    ymajorLocator = MultipleLocator(1000)
    buffer = BytesIO()
    plt.savefig(buffer, dpi=200)  
    throughput_data = buffer.getvalue()
    throughput_data_b = base64.b64encode(throughput_data)
    throughput_data_d = throughput_data_b.decode()
    imgd = "data:image/png;base64," + throughput_data_d
    plt.close()
    buffer.close()
    return imgd

@performance_blueprint.route('/throughput', methods=['GET', 'PATCH', 'OPTIONS'])
async def throughput(request):
    """
    Query throughput index API.
    """
    if request.method == 'GET':
        try:
            (agent, ) = await request.app.mysql.query('SELECT hostname FROM Agent limit 1;')
            hostname= agent[0]
        except Exception as e:
            logger.error('Query agent hostname error', exc_info=True)
            os._exit(0)
        today = aw.now()
        days = today.replace(days=-14)
        days = days.format('YYYY-MM-DD HH:mm:ss')
        default_sql = "SELECT hostname, questions, com_select, writes, create_time FROM Throughput WHERE hostname='%s' AND create_time >'%s';" % (hostname, days)
        try:
            val = await request.app.mysql.query(default_sql)
        except Exception as e:
            logger.error('Query agent throughput information error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['hostname', 'questions', 'com_select', 'writes','create_time'])
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        imgd = await throughput_dynamic_img(data)
        return json({'throughput': imgd, 'hostname': [hostname,], 'intervel': intervel})

    elif request.method in ['POST', 'PUT', 'PATCH']:
        hostname_db = request.json
        hostname = hostname_db['hostname_db'][0]
        times = hostname_db['times']
        time_start = aw.get(times[0]).format('YYYY-MM-DD HH:mm:ss')
        time_end = aw.get(times[1]).format('YYYY-MM-DD HH:mm:ss')
        query_sql = "SELECT hostname, questions, com_select, writes, create_time FROM Throughput WHERE hostname='%s' AND create_time >'%s' AND create_time <'%s';" % (hostname, time_start, time_end)
        try:
            val = await request.app.mysql.query(query_sql)
        except Exception as e:
            logger.error('Query agent throughput information error', exc_info=True)
            os._exit(0)
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['hostname', 'questions', 'com_select', 'writes','create_time'])
        imgd = await throughput_dynamic_img(data)
        return json({'throughput': imgd, 'hostname': [hostname,], 'intervel': intervel})


@performance_blueprint.route('/hostnames', methods=['GET'])
async def get_hostsinfo(request):
    """
    Get the hostname/IP interface.
    """
    if request.method == 'GET':
        hostnames_info = await request.app.mysql.query('SELECT hostname FROM Agent;')
        hostnames = [{'value': hostname[0], 'label': hostname[0]} for hostname in hostnames_info]
        return json(hostnames)

async def connections_dynamic_img(data):
    """
    Connect performance indicators to display pictures.
    """
    sns.set(color_codes=True, palette='deep', font_scale=1)
    plt.plot(data['create_time'], data['max_connections'], color='r', linestyle='--', label='max_connections')
    plt.plot(data['create_time'], data['threads_connected'], color='y', linestyle='--', label='threads_connected')
    plt.plot(data['create_time'], data['threads_running'], color='m', linestyle='--', label='threads_running')
    plt.plot(data['create_time'], data['connection_errors_internal'], color='b', linestyle='--', label='connection_errors_internal')
    plt.plot(data['create_time'], data['aborted_connects'], color='c', linestyle='--', label='aborted_connects')
    #plt.plot(data['create_time'], data['connection_errors_max_connections'], color='slategrey', linestyle='--', label='connection_errors_max_connections')
    plt.legend(loc="upper left")
    plt.title(u'Mysql connections')
    plt.legend(loc='upper left')
    ymajorLocator = MultipleLocator(1000)
    buffer = BytesIO()
    plt.savefig(buffer, dpi=200)  
    throughput_data = buffer.getvalue()
    throughput_data_b = base64.b64encode(throughput_data)
    throughput_data_d = throughput_data_b.decode()
    imgd = "data:image/png;base64," + throughput_data_d
    plt.close()
    buffer.close()
    return imgd


@performance_blueprint.route('/connections', methods=['GET', 'PATCH', 'OPTIONS'])
async def connections(request):
    """
    Connection performance index API interface.
    """
    if request.method == 'GET':
        try:
            (agent, ) = await request.app.mysql.query('SELECT hostname FROM Agent limit 1;')
            hostname= agent[0]
        except Exception as e:
            logger.error('Query agent hostname error', exc_info=True)
            os._exit(0)
        today = aw.now()
        days = today.replace(days=-14)
        days = days.format('YYYY-MM-DD HH:mm:ss')
        default_sql = "SELECT hostname, max_connections, threads_connected, threads_running, connection_errors_internal, aborted_connects, connection_errors_max_connections, create_time FROM Connections WHERE hostname='%s' AND create_time >'%s';" % (hostname, days)
        try:
            val = await request.app.mysql.query(default_sql)
        except Exception as e:
            logger.error('Query agent connections information error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['hostname', 'max_connections', 'threads_connected', 'threads_running', 'connection_errors_internal', 'aborted_connects', 'connection_errors_max_connections,','create_time'])
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        imgd = await connections_dynamic_img(data)
        return json({'connections': imgd, 'hostname': [hostname,], 'intervel': intervel})

    elif request.method in ['POST', 'PUT', 'PATCH']:
        hostname_db = request.json
        hostname = hostname_db['hostname_db'][0]
        times = hostname_db['times']
        time_start = aw.get(times[0]).format('YYYY-MM-DD HH:mm:ss')
        time_end = aw.get(times[1]).format('YYYY-MM-DD HH:mm:ss')
        query_sql = "SELECT hostname, max_connections, threads_connected, threads_running, connection_errors_internal, aborted_connects, connection_errors_max_connections, create_time FROM Connections WHERE hostname='%s' AND create_time >'%s' AND create_time <'%s';" % (hostname, time_start, time_end)
        try:
            val = await request.app.mysql.query(query_sql)
        except Exception as e:
            logger.error('Query agent connections information error', exc_info=True)
            os._exit(0)
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['hostname', 'max_connections', 'threads_connected', 'threads_running', 'connection_errors_internal', 'aborted_connects', 'connection_errors_max_connections,','create_time'])
        imgd = await connections_dynamic_img(data)
        return json({'connections': imgd, 'hostname': [hostname,], 'intervel': intervel})

async def innodb_dynamic_img(data):
    """
    Innodb buffer pool indicators to display pictures.
    """
    sns.set(color_codes=True, palette='deep', font_scale=1)
    plt.plot(data['create_time'], data['innodb_buffer_pool_read_requests'], color='r', linestyle='--', label='max_connections')
    plt.plot(data['create_time'], data['innodb_buffer_pool_reads'], color='y', linestyle='--', label='threads_connected')
    plt.legend(loc="upper left")
    plt.title(u'Buffer pool read request vs reads from disk')
    plt.legend(loc='upper left')
    ymajorLocator = MultipleLocator(1000)
    buffer = BytesIO()
    plt.savefig(buffer, dpi=200)  
    throughput_data = buffer.getvalue()
    throughput_data_b = base64.b64encode(throughput_data)
    throughput_data_d = throughput_data_b.decode()
    imgd = "data:image/png;base64," + throughput_data_d
    plt.close()
    buffer.close()
    return imgd


@performance_blueprint.route('/innodb', methods=['GET', 'PATCH', 'OPTIONS'])
async def innodb(request):
    """
    Innodb buffer pool index API interface.
    """
    if request.method == 'GET':
        try:
            (agent, ) = await request.app.mysql.query('SELECT hostname FROM Agent limit 1;')
            hostname= agent[0]
        except Exception as e:
            logger.error('Query agent hostname error', exc_info=True)
            os._exit(0)
        today = aw.now()
        days = today.replace(days=-14)
        days = days.format('YYYY-MM-DD HH:mm:ss')
        default_sql = "SELECT hostname, innodb_buffer_pool_pages_total, innodb_buffer_pool_rate, innodb_buffer_pool_read_requests, innodb_buffer_pool_reads, innodb_page_size, create_time FROM Innodb WHERE hostname='%s' AND create_time >'%s';" % (hostname, days)
        try:
            val = await request.app.mysql.query(default_sql)
        except Exception as e:
            logger.error('Query agent innodb information error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['hostname', 'innodb_buffer_pool_pages_total', 'innodb_buffer_pool_rate', 'innodb_buffer_pool_read_requests', 'innodb_buffer_pool_reads', 'innodb_page_size','create_time'])
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        imgd = await innodb_dynamic_img(data)
        return json({'innodb': imgd, 'hostname': [hostname,], 'intervel': intervel})

    elif request.method in ['POST', 'PUT', 'PATCH']:
        hostname_db = request.json
        hostname = hostname_db['hostname_db'][0]
        times = hostname_db['times']
        time_start = aw.get(times[0]).format('YYYY-MM-DD HH:mm:ss')
        time_end = aw.get(times[1]).format('YYYY-MM-DD HH:mm:ss')
        query_sql = "SELECT hostname, innodb_buffer_pool_pages_total, innodb_buffer_pool_rate, innodb_buffer_pool_read_requests, innodb_buffer_pool_reads, innodb_page_size, create_time FROM Innodb WHERE hostname='%s' AND create_time >'%s' AND create_time <'%s';" % (hostname, time_start, time_end)
        try:
            val = await request.app.mysql.query(query_sql)
        except Exception as e:
            logger.error('Query agent innodb information error', exc_info=True)
            os._exit(0)
        try:
            get_intervel_sql = 'SELECT intervel FROM Agent WHERE hostname="%s";' % hostname
            intervel = await request.app.mysql.query(get_intervel_sql)
        except Exception as e:
            logger.error('Query agent intervel error', exc_info=True)
            os._exit(0)
        data = pd.DataFrame.from_records(list(val), columns=['hostname', 'innodb_buffer_pool_pages_total', 'innodb_buffer_pool_rate', 'innodb_buffer_pool_read_requests', 'innodb_buffer_pool_reads', 'innodb_page_size','create_time'])
        imgd = await innodb_dynamic_img(data)
        return json({'innodb': imgd, 'hostname': [hostname,], 'intervel': intervel})