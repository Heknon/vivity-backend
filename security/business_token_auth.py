from typing import Tuple

import jwt
from web_framework_v2 import JwtSecurity


class BusinessJwtTokenAuth(JwtSecurity):
    def should_execute_endpoint(self, request, request_body) -> Tuple[bool, object]:
        try:
            decoded = jwt.decode(request.headers["Authorization"][8:], self.secret(), algorithms=["HS256"])
            return "business_name" in decoded and decoded["business_name"] is not None, decoded
        except:
            return False, None
