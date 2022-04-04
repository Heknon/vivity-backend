import atexit
import logging
import signal
import sys

from pymongo import ReturnDocument

import api  # must import to register package and execute its code.
from database import users_collection

logger = logging.getLogger(__name__)


def main():
    api.app.start()
    cmd = input("Enter a command: ")
    while cmd != "exit":
        handle_command(cmd)
        cmd = input("Enter a command: ")

    byebye()


def handle_command(cmd: str):
    cmd = cmd.lower().split(" ")

    if cmd[0] == "help":
        print("promote email\ndemote email\nhelp\nexit")
    elif cmd[0] == "promote":
        email = cmd[1]
        doc = users_collection.find_one_and_update({"ml": email}, {"isa": True}, return_document=ReturnDocument.AFTER, upsert=False)
        if doc is None:
            return print(f"User {email} doesn't exist")

        print(f"Set user {email} to admin")
    elif cmd[0] == "demote":
        email = cmd[1]
        doc = users_collection.find_one_and_update({"ml": email}, {"isa": False}, return_document=ReturnDocument.AFTER, upsert=False)
        if doc is None:
            return print(f"User {email} doesn't exist")

        print(f"Set user {email} to non admin")
    elif cmd[0] == "exit":
        byebye(0, 0)


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
