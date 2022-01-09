from typing import Union

from bson import ObjectId
from web_framework_v2 import QueryParameter, RequestBody, PathVariable, HttpRequest, HttpResponse, HttpStatus

from body import BusinessUpdateData, AuthorizedRouteRequestBody
from database import Business, Location, User, BusinessUser, blacklist
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth
from .. import app, auth_fail


class BusinessData:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/{business_id}")
    def get_business_data(
            business_id: PathVariable("business_id"),
            response: HttpResponse,
            get_all_categories: QueryParameter("categories", bool),
            get_all_items: QueryParameter("items", bool),
            include_category_items: QueryParameter("include_category_items", bool),
            contact: QueryParameter("contact", bool),
            location: QueryParameter("locations", bool),
            rating: QueryParameter("rating", bool),
    ):
        business_id = ObjectId(business_id)
        business = Business.get_business_by_id(business_id)

        if business is None:
            response.status = HttpStatus.NOT_FOUND
            return f"Business with id {business_id} does not exist."

        if get_all_categories is None and get_all_items is None and contact is None and location is None and rating is None:
            result = dict()

            result["name"] = business.name
            result["locations"] = business.locations
            result["items"] = business.items
            result["categories"] = business.categories if not include_category_items else business.get_categories_with_items()
            result["contact"] = business.contact
            return result

        result = dict()

        business: Business = Business.get_business_by_id(business_id)
        if get_all_categories:
            if include_category_items:
                result["categories"] = business.get_categories_with_items()
            else:
                result["categories"] = business.categories

        if get_all_items:
            result["items"] = business.items

        if contact:
            result["contact"] = business.contact

        if location:
            result["locations"] = business.locations

        if rating:
            result["rating"] = business.rating

        return result

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.patch("/business")
    def update_business_data(
            token_data: BusinessJwtTokenAuth,
            business_update_data: RequestBody(BusinessUpdateData)
    ):
        pass

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business")
    def request_business_creation(
            user: BlacklistJwtTokenAuth,
            request: HttpRequest,
            business_owner_id: RequestBody(raw_format=True),
            business_national_number: QueryParameter("business_national_number"),
            name: QueryParameter("name"),
            email: QueryParameter("email"),
            phone: QueryParameter("phone"),
            longitude: QueryParameter("longitude", float),
            latitude: QueryParameter("latitude", float),

    ):
        # TODO: Add actual verification system for business creation.
        if name is None or email is None or phone is None or longitude is None or latitude is None or business_national_number is None:
            return "Missing query parameters! Must include 'email', 'name', 'phone', 'longitude', 'latitude', 'business_national_number'."

        if len(business_owner_id) < 10:
            return "Must pass the ID of the business owner."

        user: Union[User, BusinessUser] = user
        if hasattr(user, "business_id"):
            return "You already own a business!"

        business: Business = Business.create_business(
            name,
            Location(longitude, latitude),
            email,
            phone,
            business_owner_id,
            business_national_number
        )

        user = user.promote_to_business_user(user._id, business._id)
        newToken = user.build_token(encoded=True)
        blacklist.add_to_blacklist(request.headers["Authorization"][8:])
        return {
            "new_user_token": newToken,
            "business": business
        }


class BusinessDelete:
    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/delete")
    def request_business_deletion(
            token_data: BusinessJwtTokenAuth
    ):
        pass

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/business/delete")
    def delete_business(
            token_data: BusinessJwtTokenAuth,
            authorized_route_body: RequestBody(AuthorizedRouteRequestBody)
    ):
        pass
