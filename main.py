import logging

import api  # must import to register package and execute its code.
import database
logger = logging.getLogger(__name__)


def main():
    api.app.start()


if __name__ == '__main__':
    main()

# TODO: Email system
# TODO: Implement Image system
# TODO: Implement API.
