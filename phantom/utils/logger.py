
import os
import logging

from logging.handlers import RotatingFileHandler



def setup_logger():
    logdir = os.path.expanduser('~/.phantom/logs')
    os.makedirs(logdir, exist_ok=True)
    handler = RotatingFileHandler(f"{logdir}/phantom.log", maxBytes=5*1024*1024, backupCount=3)
    logging.basicConfig(level=logging.INFO, handlers=[handler])