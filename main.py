import atexit
import logging
import signal
import sys

from web_framework_v2 import JwtSecurity

import api  # must import to register package and execute its code.
from database import s3Bucket

logger = logging.getLogger(__name__)


def main():
    print(JwtSecurity.decode_access_token('eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjYyYTcxMTdlMGI3OTg2ZmZkY2ZmMGU3NCIsIm5hbWUiOiJPcmkgSGFyZWwiLCJlbWFpbCI6InVzZXIyQGdtYWlsLmNvbSIsInBob25lIjoiMDU4NTU1MTc4NCIsImV4cCI6MTY1NTEzODE0MH0.iOuXsE-FKn2tOB_fiuK6tqMnY10t3qRSRHlWP7_Yu6Um9nk2gVV8p7Mn0_lvsDeztJrOjpzWKLK76mnp0g4JhadHNcMBeO21duSw3tBcCvSpUU-CRv9En9xEnJbCAN3rLw8FPmVDAu0x_MnAiY47CurViFa06WU--a4xQFQxYSHHHS7aCNHk07Z1Q4bqNTfEm27peyCtJnVQago4QVdIleEmAKxALjOXJqEuaueuR1Re29xIsagBnvo5HlZySBoUsLfN5PR6Tda3XKih-LlSINhfAjRQcob1IkpsOMTUpK_zcDmf0NwUiVJWL0-X1td_rOdZ0Y-2w_tFjFUWTF1MUk5iyuUzR0QypOzRRMTBlLnbYWe8l3qL-_IWJaFPetf1VgeFJlRy0muj8m2QiKiD5FeC9mAdL0iWTLStCatnFk0Z3myI34HTEx0lapG0frWHEN9nQY-HVrDGlh_LcVEQ1q-ErcCsuUeTjU71rRif77Ct-CiSmRBp7ThWP2GfOXKg3nDCgsuE_Qn3P265d_ESswC88uI3HdVvfBJlAKhr_NihGK8ill8DdyEHDmOcyPoXwzptDDMaNqW_YoWATpNtuUxdiRK08ZhToA5Nh841oooGFK1rLcWVNIOJQ85tLfC1RZwwwTStmF3uH3o4Hji5lAtyVfPUZGnoACNFfPd-hW8'))
    api.app.start()
    # cmd = input("Enter a command: ")
    # time.sleep(1)
    # while cmd != "exit":
    #     handle_command(cmd)
    #     cmd = input("Enter a command: ")

    # byebye(0, 0)


# def handle_command(cmd: str):
#     cmd = cmd.lower().split(" ")
#
#     if cmd[0] == "help":
#         print("promote email\ndemote email\nhelp\nexit")
#     elif cmd[0] == "promote":
#         email = cmd[1]
#         doc = users_collection.find_one_and_update({"ml": email}, {"isa": True}, return_document=ReturnDocument.AFTER, upsert=False)
#         if doc is None:
#             return print(f"User {email} doesn't exist")
#
#         print(f"Set user {email} to admin")
#     elif cmd[0] == "demote":
#         email = cmd[1]
#         doc = users_collection.find_one_and_update({"ml": email}, {"isa": False}, return_document=ReturnDocument.AFTER, upsert=False)
#         if doc is None:
#             return print(f"User {email} doesn't exist")
#
#         print(f"Set user {email} to non admin")
#     elif cmd[0] == "exit":
#         byebye(0, 0)


@atexit.register
def byebye(num, frame):
    print(f"Shutting down - code {num}, frame: {frame}")
    api.app.shutdown()

    exit()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, byebye)
    signal.signal(signal.SIGABRT, byebye)
    signal.signal(signal.SIGINT, byebye)
    main()

# TODO: Implement Image system
# TODO: Implement API.
# TODO: Add default responses for responses used often such as unknown business id etc..
