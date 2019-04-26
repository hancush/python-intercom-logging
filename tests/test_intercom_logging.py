#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `intercom_logging` package."""

import logging
from logging.config import dictConfig

from intercom.errors import ResourceNotFound
from intercom.event import Event
from intercom.user import User
import pytest


LOGGING_CONFIG = {
    'version': 1,  # required for future compatibility
    'formatters': {
        'console': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'intercom': {
            'level': 'INFO',
            'class': 'intercom_logging.IntercomHandler',
            'token': 'test-token',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'intercom'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


@pytest.fixture(params=[
    ({'side_effect': ResourceNotFound},
     {'return_value': User(email='new-user@email.com')}),
    ({'return_value': User(email='existing-user@email.com')}, {}),
])
def mock_intercom(mocker, request):
    mock_events = mocker.patch('intercom.client.Client.events')
    mock_events.create = mocker.MagicMock(
        return_value=Event(event_name='testing')
    )

    mock_users = mocker.patch('intercom.client.Client.users')

    find_kwargs, create_kwargs = request.param
    mock_users.find = mocker.MagicMock(**find_kwargs)
    mock_users.create = mocker.MagicMock(**create_kwargs)


def test_logging_not_fired_without_user():
    logger.info('this is a log message with no user')


def test_new_user_created(mock_intercom):
    logger.info('this is a log message with a user', extra={
        'user': {'email': 'info+testing@datamade.us'},
        'event': {
            'event_name': 'testing',
            'metadata': {
                'custom_attribute': 'hank hill',
            },
        },
    })
