from datetime import datetime
import logging

from intercom.client import Client
from intercom.errors import ResourceNotFound, IntercomError


logger = logging.getLogger(__name__)


class IntercomHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        client = kwargs.get('client_cls', Client)

        if kwargs.get('personal_access_token'):
            self.client = client(personal_access_token=kwargs['personal_access_token'])
        else:
            raise ValueError(':personal_access_token is a required configuration param')

        self.now = int(datetime.utcnow().timestamp())

        logging.Handler.__init__(self, level=kwargs.get('level', logging.NOTSET))

    def get_or_create_user(self, user_info):
        try:
            return self.client.users.find(email=user_info['email']), False

        except ResourceNotFound as e:
            user_info['signed_up_at'] = self.now
            return self.client.users.create(**user_info), True

        except IntercomError:
            logger.exception("Could not reach Intercom")

        except:
            raise

    def create_event(self, user_info, event_info):
        event_info['created_at'] = self.now
        event_info['email'] = user_info['email']

        try:
            return self.client.events.create(**event_info)

        except IntercomError as e:
            logger.exception("Could not reach Intercom")

        except:
            raise

    def emit(self, record):
        if not all((getattr(record, 'user', None),
                    getattr(record, 'event', None))):
            return

        user, created = self.get_or_create_user(record.user)
        event = self.create_event(record.user, record.event)

        print('logged {} for user {}!'.format(event, user))
