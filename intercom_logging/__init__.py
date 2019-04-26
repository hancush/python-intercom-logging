import logging

from intercom_logging.handlers import *


FORMAT = '[%(asctime)s][%(levelname)s] %(name)s ' + \
    '%(filename)s:%(funcName)s:%(lineno)d | %(message)s'

logging.basicConfig(format=FORMAT, level='ERROR')
