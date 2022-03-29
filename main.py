import atexit
import logging
import os
import signal
import sys

import api  # must import to register package and execute its code.

logger = logging.getLogger(__name__)


def main():
    api.app.start()


@atexit.register
def byebye(num, frame):
    print(f"Shutting down - code {num}, frame: {frame}")
    api.app.shutdown()

    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, byebye)
    signal.signal(signal.SIGABRT, byebye)
    signal.signal(signal.SIGINT, byebye)
    main()

# TODO: Implement Image system
# TODO: Implement API.
# TODO: Add default responses for responses used often such as unknown business id etc..
