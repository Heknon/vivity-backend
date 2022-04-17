from typing import List

from web_framework_v2 import QueryParameter, HttpResponse, HttpStatus

from api.api_utils import auth_fail
from database import Item, items_collection, businesses_collection, Business, User
from security import BlacklistJwtTokenAuth
from . import app
from .utils import applyImagesToItems


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/explore/item")
def user_explore(
        token_data: BlacklistJwtTokenAuth,
        radius: QueryParameter("radius", int),
        radius_center: QueryParameter("radius_center", list),
        response: HttpResponse
):
    user: User = token_data
    loc = parse_and_validate_query_location(radius_center)
    if loc is None:
        response.status = HttpStatus.BAD_REQUEST
        return {
            'error': "Must provide a valid 'radius_center' query parameter (type list)"
        }

    vicinity_items = search_radius_collection(loc, radius, items_collection)
    items = list(map(lambda doc: Item.document_repr_to_object(doc), vicinity_items))
    items = applyImagesToItems(*items)
    return items


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/explore/business")
def user_explore(
        token_data: BlacklistJwtTokenAuth,
        radius: QueryParameter("radius", int),
        radius_center: QueryParameter("radius_center", list),
        response: HttpResponse
):
    user: User = token_data
    loc = parse_and_validate_query_location(radius_center)
    if loc is None:
        response.status = HttpStatus.BAD_REQUEST
        return {
            'error': "Must provide a valid 'radius_center' query parameter (type list)"
        }

    vicinity_businesses = search_radius_collection(loc, radius, businesses_collection)
    return list(map(lambda doc: Business.document_repr_to_object(doc), vicinity_businesses))


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/search")
def user_feed(
        token_data: BlacklistJwtTokenAuth,
        query: QueryParameter("query", str),
        response: HttpResponse
):
    # TODO: Partial text search
    if query is None:
        response.status = HttpStatus.BAD_REQUEST
        return {
            'error': "Must provide a valid 'query' query parameter (type list)"
        }

    search_result = items_collection.find({
        "$text": {
            "$search": query
        }
    }, {"score": {"$meta": "textScore"}})

    search_result = search_result.sort([("score", {"$meta": "textScore"})])
    items = list(map(lambda doc: Item.document_repr_to_object(doc), search_result))
    return applyImagesToItems(*items)


def search_radius_collection(
        location: List[float],
        radius: float,
        collection
):
    return collection.find({
        "loc": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": location
                },
                "$maxDistance": (radius if radius is not None else 1000) + 1000  # add to radius to account for inaccuracies
            }
        }
    })


def parse_and_validate_query_location(location: List[str]):
    if not isinstance(location, list):
        return None

    loc = location if location is not None and len(location) == 2 else []
    validated_loc = []

    for pos in loc:
        if pos is not None:
            try:
                validated_loc.append(float(pos))
            except:
                continue

    loc = validated_loc if len(validated_loc) == 2 else None
    return loc


