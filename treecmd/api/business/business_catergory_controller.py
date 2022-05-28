from bson import ObjectId
from web_framework_v2 import PathVariable, RequestBody, QueryParameter, HttpResponse, HttpStatus

from body import UpdateCategoryData
from database import Business, BusinessUser, Category
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth
from .. import app


@BlacklistJwtTokenAuth()
@app.get("/business/{business_id}/category/{category}")
def get_category_data(
        business_id: PathVariable("business_id"),
        response: HttpResponse,
        category: PathVariable("category"),
        include_items: QueryParameter("include_item", bool)
):
    business = Business.get_business_by_id(ObjectId(business_id))

    if business is None:
        response.status = HttpStatus.NOT_FOUND
        return f"No business with ID {business_id} exists"

    return business.get_category_by_name(category, include_items)


@BusinessJwtTokenAuth()
@app.post("/business/category/{category}")
def create_category(
        token_data: BusinessJwtTokenAuth,
        category: PathVariable("category"),
        body: RequestBody(),
        res: HttpResponse
):
    user: BusinessUser = token_data
    business = Business.get_business_by_id(user.business_id)

    cat = Category(
        business_id=business.id,
        name=category,
        items_ids=list(map(lambda item_id: ObjectId(item_id), body.get("item_ids", [])))
    )
    business.add_category(cat)

    res.status = HttpStatus.CREATED
    return cat


@BusinessJwtTokenAuth()
@app.patch("/business/category/{category}")
def update_category(
        token_data: BusinessJwtTokenAuth,
        category: PathVariable("category"),
        category_data: RequestBody(UpdateCategoryData)
):
    user: BusinessUser = token_data
    business = Business.get_business_by_id(user.business_id)
    cat_data: UpdateCategoryData = category_data

    add_ids = list(filter(lambda item_id: item_id not in cat_data.remove_item_ids, cat_data.add_item_ids))
    remove_ids = list(filter(lambda item_id: item_id not in cat_data.add_item_ids, cat_data.remove_item_ids))
    cat = business.get_category_by_name(category, False).update_fields(
        name=cat_data.name,
        added_ids=list(map(lambda item_id: ObjectId(item_id), add_ids)),
        removed_ids=list(map(lambda item_id: ObjectId(item_id), remove_ids)),
    )

    return cat


@BusinessJwtTokenAuth()
@app.delete("/business/category/{category}")
def delete_category(
        token_data: BusinessJwtTokenAuth,
        category: PathVariable("category"),
        response: HttpResponse
):
    user: BusinessUser = token_data
    business = Business.get_business_by_id(user.business_id)

    business.remove_category(category)
    response.status = HttpStatus.NO_CONTENT
