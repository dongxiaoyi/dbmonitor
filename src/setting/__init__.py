import sys
import os
import yaml
from collections.abc import MutableMapping
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import Singleton

DEV = False

DEV_CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_dev.yml')
PRO_CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_pro.yml')

class Config(metaclass=Singleton):
    """
    The configuration of the dictionary format is loaded here.
    
    returns: The dictionary format for the return configuration.
    """
    def __init__(self, switch=DEV, default_config=None):
        """
        :param switch: Configuration file switch for development or generated environment.
        :param default_config: Configuration of default dict when you can't find a configuration file.
        """
        self.__switch = switch
        self.__config = default_config

    @property
    def load_config(self):
        """
        Load configuration method.
        """
        if self.__switch is False:
            try:
                os.path.exists(PRO_CONFIG_FILE)
            except FileNotFoundError as e:
                return self.__config
            else:
                with open(PRO_CONFIG_FILE, 'r') as conf_f:
                    conf_dict = yaml.load(conf_f)
                return conf_dict
        elif self.__switch is True:
            try:
                os.path.exists(DEV_CONFIG_FILE)
            except FileNotFoundError as e:
                return self.__config
            else:
                with open(DEV_CONFIG_FILE, 'r') as conf_f:
                    conf_dict = yaml.load(conf_f)
                return conf_dict
        else:
            raise AttributeError('Attribute "switch" must be False/True.')

    @load_config.setter
    def load_config(self, value):
        raise AttributeError('Method "get_config" cant\'t be set.')
        
    def __call__(self):
        """
        Direct call back to the dictionary format of the load configuration.
        """
        return self.load_config

dictConfig = Config()()
"""
Dictionary format of the configuration.
"""


class SetupConfig(dict):
    """
    Access to dictionary objects in an attribute format.
    """
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)

    def __getattr__(self, key):
        if not isinstance(self[key], MutableMapping):
            return self[key]
        else:
            return SetupConfig(self[key])

Config = SetupConfig(dictConfig)
