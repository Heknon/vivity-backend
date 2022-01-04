from body import ItemCreation, ItemUpdate
from web_framework_v2 import RequestBody, PathVariable, QueryParameter

from body import Review
from .. import app
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth


@BlacklistJwtTokenAuth()
@app.get("/business/{business_id}/item")
def get_items(
        business_id: PathVariable("business_id"),
        item_ids: QueryParameter("item_ids", list)
):
    pass


@BusinessJwtTokenAuth()
@app.post("/business/item")
def create_item(
        token_data: BusinessJwtTokenAuth,
        item_data: RequestBody(ItemCreation)
):
    pass


""" SPECIFIC ITEM """


@BusinessJwtTokenAuth()
@app.patch("/business/item/{item_id}")
def update_item(
        token_data: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id"),
        update_data: RequestBody(ItemUpdate)
):
    pass


@BusinessJwtTokenAuth()
@app.delete("/business/item/{item_id}")
def delete_item(
        token_data: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id")
):
    pass


"""ITEM REVIEWS"""


@BlacklistJwtTokenAuth()
@app.get("/business/{business_id}/item/{item_id}/review")
def get_item_reviews(
        business_id: PathVariable("business_id"),
        item_id: PathVariable("item_id")
):
    pass


@BlacklistJwtTokenAuth()
@app.post("/business/{business_id}/item/{item_id}/review")
def add_item_review(
        token_data: BlacklistJwtTokenAuth,
        business_id: PathVariable("business_id"),
        item_id: PathVariable("item_id"),
        review_data: RequestBody(Review)
):
    pass


@BlacklistJwtTokenAuth()
@app.delete("/business/{business_id}/item/{item_id}/review")
def delete_item_review(
        token_data: BlacklistJwtTokenAuth,
        business_id: PathVariable("business_id"),
        item_id: PathVariable("item_id"),
        review_id: RequestBody(Review)
):
    pass
