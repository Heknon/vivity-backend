from bson import ObjectId
from pymongo import ReturnDocument
from web_framework_v2 import RequestBody, PathVariable, QueryParameter, HttpResponse, HttpStatus

from body import ItemCreation, ItemUpdate
from body import Review
from database import Item, ItemStoreFormat, Business, BusinessUser, User, items_collection
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth
from .. import app, auth_fail


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/business/{business_id}/item")
def get_items(
        item_ids: QueryParameter("item_ids", list)
):
    return Item.get_items(item_ids)


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/business/item")
def get_items(
        item_ids: QueryParameter("item_ids", list)
):
    if not isinstance(item_ids, list):
        item_ids = [item_ids]

    return Item.get_items(*list(map(lambda item_id: ObjectId(item_id), item_ids)))


@BusinessJwtTokenAuth(on_fail=auth_fail)
@app.post("/business/item")
def create_item(
        token_data: BusinessJwtTokenAuth,
        item_data: RequestBody(ItemCreation),
        res: HttpResponse
):
    item_creation_data: ItemCreation = item_data
    user: BusinessUser = token_data
    business = Business.get_business_by_id(user.business_id)

    result = Item.save_item(
        business_id=user.business_id,
        business_name=business.name,
        price=item_creation_data.price,
        images=[],
        preview_image=-1,
        reviews=[],
        item_store_format=ItemStoreFormat(
            item_id=None,
            title=item_creation_data.title,
            subtitle=item_creation_data.subtitle,
            description="",
            modification_buttons=[]
        ),
        brand=item_creation_data.brand,
        category=item_creation_data.category,
        tags=item_creation_data.tags,
        stock=0
    )

    business.add_item(result.id)
    res.status = HttpStatus.CREATED
    return result


""" SPECIFIC ITEM """


@BusinessJwtTokenAuth(on_fail=auth_fail)
@app.post("/business/item/{item_id}/stock")
def update_item_stock(
        raw_user: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id"),
        stock: QueryParameter("stock", int),
        res: HttpResponse
):
    user: BusinessUser = raw_user
    if stock is None or not isinstance(stock, int) or stock >= 10000:
        res.status = HttpStatus.BAD_REQUEST
        return {
            "error": "Must pass query parameter 'stock' and it must be an integer below 10000"
        }

    _id = ObjectId(item_id)
    item: Item = Item.get_item(_id)
    if item is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {
            "error": f"Item with id {item_id} doesn't exist"
        }

    if user.business_id != item.business_id:
        res.status = HttpStatus.UNAUTHORIZED
        return {
            "error": f"Item with id {item_id} doesn't exist"
        }

    item_doc = items_collection.find_one_and_update({"_id": _id}, {"$set": {Item.LONG_TO_SHORT["stock"]: stock}}, return_document=ReturnDocument.AFTER)
    if item_doc is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {
            "error": f"Item with id {item_id} doesn't exist"
        }

    return Item.document_repr_to_object(item_doc)


@BusinessJwtTokenAuth(on_fail=auth_fail)
@app.patch("/business/item/{item_id}")
def update_item(
        token_data: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id"),
        update_data: RequestBody(ItemUpdate),
        res: HttpResponse
):
    user: BusinessUser = token_data
    item_update_data: ItemUpdate = update_data

    item = Item.get_item(ObjectId(item_id))
    if item.business_id != user.business_id:
        res.status = HttpStatus.UNAUTHORIZED
        return

    add_tags = list(filter(lambda tag: tag not in item_update_data.remove_tags, item_update_data.add_tags))
    remove_tags = list(filter(lambda tag: tag not in item_update_data.add_tags, item_update_data.remove_tags))

    item = item.update_fields(
        title=item_update_data.title,
        subtitle=item_update_data.subtitle,
        description=item_update_data.description,
        price=item_update_data.price,
        brand=item_update_data.brand,
        category=item_update_data.category,
        stock=item_update_data.stock,
        added_tags=add_tags,
        removed_tags=remove_tags,
        add_image=item_update_data.add_image_id,
    )

    if item_update_data.remove_image is not None and 0 < item_update_data.remove_image < len(item.images):
        item = item.remove_image(item_update_data.remove_image)

    return item


@BusinessJwtTokenAuth(on_fail=auth_fail)
@app.delete("/business/item/{item_id}")
def delete_item(
        token_data: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id"),
        res: HttpResponse
):
    user: BusinessUser = token_data

    Item.delete_item(item_id)
    Business.get_business_by_id(user.business_id).remove_item(item_id)
    res.status = HttpStatus.NO_CONTENT
    return


"""ITEM REVIEWS"""


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.get("/business/{business_id}/item/{item_id}/review")
def get_item_reviews(
        item_id: PathVariable("item_id")
):
    return Item.get_item(item_id).reviews


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.post("/business/{business_id}/item/{item_id}/review")
def add_item_review(
        token_data: BlacklistJwtTokenAuth,
        item_id: PathVariable("item_id"),
        review_data: RequestBody(Review),
        anonymous: QueryParameter("anonymous", parameter_type=bool),
        res: HttpResponse
):
    review: Review = review_data
    user: User = token_data

    Item.get_item(item_id).add_review(Review(
        poster_id=user.id,
        pfp_id=user.profile_picture.image_id,
        poster_name="" if anonymous else user.name,
        rating=review.rating,
        text_content=review.text_content,
        image_ids=review.image_ids
    ))

    res.status = HttpStatus.CREATED


@BlacklistJwtTokenAuth()
@app.delete("/business/{business_id}/item/{item_id}/review")
def delete_item_review(
        token_data: BlacklistJwtTokenAuth,
        item_id: PathVariable("item_id"),
        res: HttpResponse
):
    user: User = token_data
    Item.get_item(item_id).remove_review(user.id)
    res.status = HttpStatus.NO_CONTENT
