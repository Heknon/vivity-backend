from web_framework_v2 import JwtTokenAuth, QueryParameter

from api.api_utils import auth_fail
from . import app


@JwtTokenAuth(on_fail=auth_fail)
@app.get("/user/explore")
def user_explore(
        token_data: JwtTokenAuth,
        radius: QueryParameter("radius", int),
        radius_center_longitude: QueryParameter("radius_center_longitude", float),
        radius_center_latitude: QueryParameter("radius_center_latitude", float),
        category: QueryParameter("category", str),
        query: QueryParameter("query", str),
):
    pass


@JwtTokenAuth(on_fail=auth_fail)
@app.get("/user/feed")
def user_feed(
        token_data: JwtTokenAuth,
        category: QueryParameter("category", str),
        query: QueryParameter("query", str)
):
    pass
