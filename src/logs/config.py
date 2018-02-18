from __future__ import absolute_import
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import yaml
import os
import sys
import time

CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging.yml')
ERRORLOG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'error.log')
