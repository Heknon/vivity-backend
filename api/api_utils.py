import json
import logging

from web_framework_v2 import HttpStatus, HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


def auth_fail(req: HttpRequest, res: HttpResponse, data):
    logger.debug(f"Failed authentication for {json.loads(req.body)['email']}: {data}\t\t-\tSetting status to {HttpStatus.UNAUTHORIZED}.")

    res.status = HttpStatus.UNAUTHORIZED
    return "Unauthorized"
