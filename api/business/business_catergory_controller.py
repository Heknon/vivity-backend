from web_framework_v2 import JwtTokenAuth, PathVariable, RequestBody

from .. import app
from body import UpdateCategoryData
from security.token_security import BusinessJwtTokenAuth


@JwtTokenAuth()
@app.get("/business/{business_id}/category/{category}")
def get_category_data(
        business_id: PathVariable("business_id"),
        category: PathVariable("category")
):
    pass


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
