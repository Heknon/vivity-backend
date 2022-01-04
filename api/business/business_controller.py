from web_framework_v2 import JwtTokenAuth, QueryParameter, RequestBody, PathVariable

from .. import app
from body import BusinessUpdateData, AuthorizedRouteRequestBody
from security.business_token_auth import BusinessJwtTokenAuth


class BusinessData:
    @staticmethod
    @JwtTokenAuth()
    @app.get("/business/{business_id}")
    def get_business_data(
            business_id: PathVariable("business_id"),
            get_all_categories: QueryParameter("all_categories", bool),
            get_all_items: QueryParameter("all_items", bool),
            category_ids: QueryParameter("categories", list),
            item_ids: QueryParameter("item", list),
            contact: QueryParameter("contact", bool),
            location: QueryParameter("categories", bool),
            rating: QueryParameter("rating", bool),
    ):
        pass

    @staticmethod
    @BusinessJwtTokenAuth()
    @app.patch("/business")
    def update_business_data(
            token_data: BusinessJwtTokenAuth,
            business_update_data: RequestBody(BusinessUpdateData)
    ):
        pass

    @staticmethod
    @JwtTokenAuth()
    @app.post("/business")
    def request_business_creation(
            business_owner_id: RequestBody(raw_format=True),
            business_national_number: QueryParameter("business_national_number")
    ):
        pass


class BusinessDelete:
    @staticmethod
    @BusinessJwtTokenAuth()
    @app.post("/business/delete")
    def request_business_deletion(
            token_data: BusinessJwtTokenAuth
    ):
        pass

    @staticmethod
    @BusinessJwtTokenAuth()
    @app.delete("/business/delete")
    def delete_business(
            token_data: BusinessJwtTokenAuth,
            authorized_route_body: RequestBody(AuthorizedRouteRequestBody)
    ):
        pass
