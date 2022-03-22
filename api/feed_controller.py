from web_framework_v2 import QueryParameter

from api.api_utils import auth_fail
from database import User, items_collection, Item
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
    user: User = token_data
    loc = [radius_center_latitude, radius_center_longitude]

    vicinity_items = items_collection.find({
        "loc": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": loc
                },
                "$maxDistance": radius + 1000  # add to radius to account for inaccuracies
            }
        }
    })
    return list(map(lambda doc: Item.document_repr_to_object(doc), vicinity_items))


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/user/feed")
def user_feed(
        token_data: BlacklistJwtTokenAuth,
        category: QueryParameter("category", str),
        query: QueryParameter("query", str)
):
    pass
