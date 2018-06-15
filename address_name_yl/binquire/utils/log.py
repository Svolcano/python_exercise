#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import logging.config

try:
    from settings import LOG_LEVEL
except ImportError:
    LOG_LEVEL = 'INFO'

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file_handler': {
            'level': 'INFO',
            'filename': '/tmp/mylogfile.log',
            'class': 'logging.FileHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'aiohttp': {
            'level': 'ERROR',
        },
        'asyncio': {
            'level': 'ERROR',
        },
        'urllib3': {
            'level': 'ERROR',
        },
        'requests': {
            'level': 'ERROR',
        },
        '':{
            'level':LOG_LEVEL.upper(),
        }
    }
}


def getLogger(logger,level=LOG_LEVEL):
    """Get logger by name."""
    if isinstance(logger, str):
        logging.config.dictConfig(DEFAULT_LOGGING)
        logger = logging.getLogger(logger)
    if not logger.handlers:
        logger.addHandler(_get_handler(level=LOG_LEVEL))
    return logger


def _get_handler(filename='', enable=True, level=LOG_LEVEL):
    """ Return a log handler object according to settings """
    if filename:
        handler = logging.FileHandler(filename)
    elif enable:
        handler = logging.StreamHandler()
    else:
        handler = logging.NullHandler()

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )
    handler.setFormatter(formatter)
    handler.setLevel(getattr(logging, level.upper()))

    return handler
