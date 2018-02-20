**Overview**
A simple view of the part of the MySQL performance index DEMO.

**Main technology stack**
- Python 3.6
- asyncio
- aioredis
- aiomysql
- Sanic
- pandas
- matplotlib
- seaborn
- Vue.js 2.x
- axios

**Configurations**
- settings
1. You can configure the server side and the client configuration.
2. Configure the class to see setting/\_\_init\_\_.py

```
cd /src/setting
vim config_pro.yml
```

- log
1. In src/logs/loging.yml, you can configure the dict configuration of the logging module.
2. In src/logs/config.py you can configure the logging.yml file path, as well as the error log file storage path.
3. In src/logs/\_\_init\_\_.py, you can configure the default log configuration.

**Usage**
- Run server
```
cd src/server
python3.6 run.py
```

- Run client
```
cd src/agent
python3.6 run.py
```

- Run frontend
```
cd src/front/dist
http-server
```
