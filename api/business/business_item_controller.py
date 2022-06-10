import base64

from bson import ObjectId
from pymongo import ReturnDocument
from web_framework_v2 import RequestBody, PathVariable, QueryParameter, HttpResponse, HttpStatus

import database as database
from body import ItemCreation, ItemUpdate
from body import Review
from database import Item, ItemStoreFormat, Business, BusinessUser, User, items_collection, ModificationButton, Image, s3Bucket
from database.business.item.item_metrics import ItemMetrics
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth
from .. import app, auth_fail, REVIEW_IMAGE_AWS_FOLDER, ITEM_IMAGE_AWS_FOLDER
from ..utils import applyImagesToItems


@app.post("/business/items")
def get_items(
        item_ids: RequestBody(),
        include_images: QueryParameter('include_images', bool)
):
    if not isinstance(item_ids, list):
        item_ids = [item_ids]

    items = Item.get_items(*list(map(lambda item_id: ObjectId(item_id), item_ids)))
    include_images = include_images if include_images is not None and isinstance(include_images, bool) else False
    if include_images is not None and include_images:
        items = applyImagesToItems(*items)
    else:
        for item in items:
            item.images = []

    return items


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
        business_name=business.name.strip(),
        price=item_creation_data.price,
        images=[],
        preview_image=-1,
        reviews=[],
        item_store_format=ItemStoreFormat(
            item_id=None,
            title=item_creation_data.title.strip(),
            subtitle=item_creation_data.subtitle.strip(),
            description="",
            modification_buttons=[]
        ),
        brand=item_creation_data.brand.strip(),
        category=item_creation_data.category.strip(),
        tags=list(map(lambda x: x.lower().strip(), item_creation_data.tags)),
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

    if index is not None and not isinstance(index, int):
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
    if item.business_id != user.business_id:
        res.status = HttpStatus.UNAUTHORIZED
        return

    if index is None:
        index = len(item.images)
    elif index > len(item.images):
        res.status = HttpStatus.BAD_REQUEST
        return {
            f"Can set images in index range of 0-{len(item.images)}"
        }

    result = Image.upload(image, folder_name="items/")
    if result.image_id is None:
        res.status = HttpStatus.INTERNAL_SERVER_ERROR
        return {
            "error": "failed"
        }

    return applyImagesToItems(item.add_image(result, index))[0]


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
    image.delete_image()
    return applyImagesToItems(item)[0]


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

    tags = list(map(lambda tag: tag.lower().strip(), set(item_update_data.tags))) if item_update_data.tags is not None else None

    item = item.update_fields(
        title=item_update_data.title.strip(),
        subtitle=item_update_data.subtitle.strip(),
        description=item_update_data.description.strip(),
        price=item_update_data.price,
        brand=item_update_data.brand.strip(),
        category=item_update_data.category.strip(),
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
    return {
        "success": True
    }


"""ITEM REVIEWS"""


# TODO: Remove business sensitive data for normal users


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

    imgs = []
    for image in review.images if review.images is not None else []:
        data = base64.b64decode(image)
        if len(data) < 100:
            continue

        img = Image.upload(data, REVIEW_IMAGE_AWS_FOLDER)
        imgs.append(img)

    item = Item.get_item(item_id).add_review(database.Review(
        poster_id=user.id,
        pfp_image=user.profile_picture,
        poster_name="" if anonymous else user.name,
        rating=review.rating,
        text_content=review.text_content,
        images=list(map(lambda x: x.image_id, imgs))
    ))

    res.status = HttpStatus.CREATED
    return item


@BlacklistJwtTokenAuth()
@app.delete("/business/{business_id}/item/{item_id}/review")
def delete_item_review(
        token_data: BlacklistJwtTokenAuth,
        item_id: PathVariable("item_id"),
        res: HttpResponse
):
    user: User = token_data
    item = Item.get_item(item_id).remove_review(user.id)
    res.status = HttpStatus.NO_CONTENT
    return item
