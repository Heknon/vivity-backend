from bson import ObjectId
from web_framework_v2 import PathVariable, RequestBody, QueryParameter, HttpResponse, HttpStatus

from database import Business
from .. import app
from body import UpdateCategoryData
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth


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


@BusinessJwtTokenAuth()
@app.post("/business/category/{category}")
def create_category(
        token_data: BusinessJwtTokenAuth,
        category: PathVariable("category"),
        item_ids: RequestBody()
):
    pass


@BusinessJwtTokenAuth()
@app.patch("/business/category/{category}")
def update_category(
        token_data: BusinessJwtTokenAuth,
        category: PathVariable("category"),
        category_data: RequestBody(UpdateCategoryData)
):
    pass


@BusinessJwtTokenAuth()
@app.delete("/business/category/{category}")
def delete_category(
        token_data: BusinessJwtTokenAuth,
        category: PathVariable("category")
):
    pass
