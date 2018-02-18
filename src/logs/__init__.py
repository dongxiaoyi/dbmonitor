import logging
import logging.config
from logging.handlers import RotatingFileHandler
import yaml
import os
import sys
import time

from .config import CONFIG, ERRORLOG_PATH
from utils import Singleton

default_config = {'version': 1,
           'formatters': {'log_formatter': 
                                         {'format': '%(asctime)-15s %(levelname)s %(filename)s [line:%(lineno)d]  %(process)d %(message)s'}
                         }, 
            'handlers':  {'console': 
                                    {'class': 'logging.StreamHandler', 
                                     'level': 'DEBUG', 
                                     'formatter': 'log_formatter', 
                                     'stream': 'ext://sys.stdout'
                                     }, 
                          'log_err': 
                                    {'class': 'logging.handlers.TimedRotatingFileHandler', 
                                     'when': 'H',
                                     'interval': 6, 
                                     'level': 'ERROR', 
                                     'formatter': 'log_formatter', 
                                     'filename': 'error.log', 
                                     'utc': True, 
                                     'backupCount': 5
                                     }
                         }, 
            'loggers': {'agent': 
                                        {'level': 'DEBUG', 
                                         'handlers': ['console', 'log_err'], 
                                         'propagate': True
                                        }
                       }
            }

default_error_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'error.log')


class Logger(metaclass=Singleton):
    """
    Log manager
    :param load_config: Configuration of dictionary format.
    :param default_save_path: Log default save address.
    """
    def __init__(self, load_config=default_config, default_save_path=default_error_path):
        self.__config = default_config
        self.__save_path = default_save_path

    @property
    def get_logger(self):
        """"
        Get a Logger object.
        """
        config = self.load_config
        logging.config.dictConfig(config)
        return logging.getLogger('agent')

    @get_logger.setter
    def get_logger(self, value):
        raise AttributeError('Attribute "get_logger" is Readonly')
    
    @property
    def load_config(self):
        if not os.path.exists(CONFIG):
            return self.__config
        else:
            with open(CONFIG, 'r') as conf_f:
                dict_conf = yaml.load(conf_f)
        error_file = self.load_save_path
        dict_conf['handlers']['log_err'].update({'filename': error_file})
        self.__config = dict_conf
        return self.__config

    @load_config.setter
    def load_config(self, value):
        raise AttributeError('Attribute "load_config" is Readonly')

    @property
    def load_save_path(self):
        if os.path.exists(ERRORLOG_PATH):
            self.__save_path = ERRORLOG_PATH
        return self.__save_path

    @load_save_path.setter
    def load_save_path(self, value):
        raise AttributeError('Attribute "load_save_path" is Readonly')
    
    def __call__(self):
        return self.get_logger

logger = Logger()()

__all__ = ['CONFIG', 'ERRORLOG_PATH', 'logger']
