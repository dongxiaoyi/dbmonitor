from sanic import Sanic
from sanic import Blueprint
from sanic.response import json, text, HTTPResponse, html
from sanic_mysql import SanicMysql
from sanic_redis import SanicRedis
from sanic_cors import CORS
import pandas as pd
import aiomysql
import asyncio
import os
import sys
from datetime import datetime

from performance.views import performance_blueprint

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from setting import Config as settings

# create a Sanic instance
app = Sanic(__name__)

# register blueprint
app.register_blueprint(performance_blueprint)

# Cross domain problem solving
CORS(app, automatic_options=True)

# update sanic configration for use SanicMysql(a mysqldriver based aiomysql)
db = settings.SERVER_DB
app.config.update(dict(MYSQL=dict(host=db.host,
                                  port=db.port,
                                  user=db.user, 
                                  password=db.password,
                                  db=db.db)))
SanicMysql(app)                                

app.config.update(
        {
            'REDIS': {
                'address': ('127.0.0.1', 6379),
                # 'db': 0,
                # 'password': 'password',
                # 'ssl': None,
                # 'encoding': None,
                # 'minsize': 1,
                # 'maxsize': 10
            }
        }
    )
redis = SanicRedis(app)

app.run(host="0.0.0.0", port=8000, debug=True, workers=1)