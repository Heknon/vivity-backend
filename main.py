import logging

import api  # must import to register package and execute its code.
from database import ModificationButtonDataType

logger = logging.getLogger(__name__)


def main():
    api.app.start()


if __name__ == '__main__':
    main()

# TODO: Implement Image system
# TODO: Implement API.
# TODO: Add default responses for responses used often such as unknown business id etc..
