#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `intercom_logging` package."""

import logging
from logging.config import dictConfig

from intercom.errors import ResourceNotFound
from intercom.event import Event
from intercom.user import User
import pytest

from intercom_logging import IntercomHandler
from intercom_logging.handlers import Client as IntercomClient


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
            'personal_access_token': 'test-token',
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


@pytest.fixture
def user():
    return User(email='some-user@email.com')


@pytest.fixture
def event():
    return Event(event_name='testing')


@pytest.fixture
def mock_intercom(mocker, event):
    mock_events = mocker.patch('intercom.client.Client.events')
    mock_events.create = mocker.MagicMock(return_value=event)

    return mocker.patch('intercom.client.Client.users')


@pytest.fixture
def mock_intercom_new_user(mock_intercom, mocker, user):
    mock_intercom.find = mocker.MagicMock(side_effect=ResourceNotFound)
    mock_intercom.create = mocker.MagicMock(return_value=user)


@pytest.fixture
def mock_intercom_existing_user(mock_intercom, mocker, user):
    mock_intercom.find = mocker.MagicMock(return_value=user)


def test_logging_not_fired_without_user():
    logger.info('this is a log message with no user')


def test_new_user_created(mock_intercom_new_user):
    logger.info('this is a log message with a new user', extra={
        'user': {'email': 'info+testing@datamade.us'},
        'event': {
            'event_name': 'testing',
            'metadata': {
                'custom_attribute': 'hank hill',
            },
        },
    })


def test_existing_user_found(mock_intercom_existing_user):
    logger.info('this is a log message with an existing user', extra={
        'user': {'email': 'info+testing@datamade.us'},
        'event': {
            'event_name': 'testing',
            'metadata': {
                'custom_attribute': 'bobby hill',
            },
        },
    })
