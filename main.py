import logging

import api  # must import to register package and execute its code.
import database
from communication import email_service

logger = logging.getLogger(__name__)


def main():
    api.app.start()


if __name__ == '__main__':
    main()

# TODO: Implement Image system
# TODO: Implement API.
