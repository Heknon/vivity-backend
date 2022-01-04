from web_framework_v2 import QueryParameter

from api.api_utils import auth_fail
from security import BlacklistJwtTokenAuth
from . import app


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/user/explore")
def user_explore(
        token_data: BlacklistJwtTokenAuth,
        radius: QueryParameter("radius", int),
        radius_center_longitude: QueryParameter("radius_center_longitude", float),
        radius_center_latitude: QueryParameter("radius_center_latitude", float),
        category: QueryParameter("category", str),
        query: QueryParameter("query", str),
):
    pass


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/user/feed")
def user_feed(
        token_data: BlacklistJwtTokenAuth,
        category: QueryParameter("category", str),
        query: QueryParameter("query", str)
):
    pass
