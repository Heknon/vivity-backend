import json
import logging

from web_framework_v2 import HttpStatus, HttpRequest, HttpResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def auth_fail(req: HttpRequest, res: HttpResponse, data):
    logger.debug(
        f"Failed authentication for {json.loads(req.body).get('email', None) if type(req.body) is not bytes else None}: {data}\t\t-\tSetting status to {HttpStatus.UNAUTHORIZED}."
    )

    res.status = HttpStatus.UNAUTHORIZED
    res.content_type = "application/json"
    return json.dumps({
        "error": "Unauthorized"
    })
