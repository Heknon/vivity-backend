from bson import ObjectId
from pymongo import ReturnDocument
from web_framework_v2 import RequestBody, PathVariable, QueryParameter, HttpResponse, HttpStatus

from body import ItemCreation, ItemUpdate
from body import Review
from database import Item, ItemStoreFormat, Business, BusinessUser, User, items_collection, ModificationButton, Image
from database.business.item.item_metrics import ItemMetrics
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
        stock=0,
        metrics=ItemMetrics(
            item_id=None,
            orders=0,
            likes=0,
            views=0
        ),
        location=business.location
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
    if stock is None or not isinstance(stock, int) or stock >= 10000 or stock < 0:
        res.status = HttpStatus.BAD_REQUEST
        return {
            "error": "Must pass query parameter 'stock' and it must be an integer below 10000 and above 0"
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

    item_doc = items_collection.find_one_and_update({"_id": _id}, {"$set": {Item.LONG_TO_SHORT["stock"]: stock}},
                                                    return_document=ReturnDocument.AFTER)
    if item_doc is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {
            "error": f"Item with id {item_id} doesn't exist"
        }

    return Item.document_repr_to_object(item_doc)


@BusinessJwtTokenAuth(on_fail=auth_fail)
@app.post("/business/item/{item_id}/image")
def swap_image_of_item(
        token_data: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id"),
        index: QueryParameter("index", int),
        image: RequestBody(raw_format=True),
        res: HttpResponse
):
    user: BusinessUser = token_data

    if not isinstance(index, int):
        return {
            "error": "must supply query parameter 'index' as an integer"
        }

    if len(image) < 100:
        res.status = HttpStatus.BAD_REQUEST
        return {
            "error": "Image must be at least 100 bytes"
        }

    item_id = ObjectId(item_id)
    item = Item.get_item(item_id)
    if index is None:
        index = len(item.images)

    if item.business_id != user.business_id:
        res.status = HttpStatus.UNAUTHORIZED
        return

    result = Image.upload(image, folder_name="items/")
    if result.image_id is None:
        res.status = HttpStatus.INTERNAL_SERVER_ERROR
        return {
            "error": "failed"
        }

    if index < len(item.images):
        item.images[index].delete_image("items/")

    return item.add_image(result, index)


@BusinessJwtTokenAuth(on_fail=auth_fail)
@app.delete("/business/item/{item_id}/image")
def remove_image_from_item(
        token_data: BusinessJwtTokenAuth,
        item_id: PathVariable("item_id"),
        index: QueryParameter("index", int),
        res: HttpResponse,
):
    user: BusinessUser = token_data
    if index is None or not isinstance(index, int):
        res.status = HttpStatus.BAD_REQUEST
        return {
            "error": "must supply query parameter 'index' as an integer"
        }

    item_id = ObjectId(item_id)
    item = Item.get_item(item_id)

    if item.business_id != user.business_id:
        res.status = HttpStatus.UNAUTHORIZED
        return

    if index >= len(item.images):
        res.status = HttpStatus.BAD_REQUEST
        return {
            "error": "No such index"
        }

    image = item.images[index]
    item = item.remove_image(index)
    image.delete_image("items/")
    return item


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

    item_id = ObjectId(item_id)
    item = Item.get_item(item_id)
    if item.business_id != user.business_id:
        res.status = HttpStatus.UNAUTHORIZED
        return

    add_tags = set(item_update_data.add_tags if item_update_data.add_tags is not None else [])
    remove_tags = set(item_update_data.remove_tags if item_update_data.remove_tags is not None else [])

    add_tags = list(filter(lambda tag: tag not in remove_tags, add_tags))
    remove_tags = list(filter(lambda tag: tag not in add_tags, remove_tags))
    tags = set(item_update_data.tags + add_tags)
    tags = list(filter(lambda tag: tag not in remove_tags, tags))

    item = item.update_fields(
        title=item_update_data.title,
        subtitle=item_update_data.subtitle,
        description=item_update_data.description,
        price=item_update_data.price,
        brand=item_update_data.brand,
        category=item_update_data.category,
        stock=item_update_data.stock,
        tags=tags,
        modification_buttons=list(
            map(lambda x: ModificationButton.document_repr_to_object(x, True, item_id=item_id), item_update_data.modification_buttons))
    )

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
