import base64
from typing import Union

from bson import ObjectId
from web_framework_v2 import QueryParameter, RequestBody, PathVariable, HttpRequest, HttpResponse, HttpStatus

from body import BusinessUpdateData, AuthorizedRouteRequestBody
from body.business_create import BusinessCreate
from database import Business, Location, User, BusinessUser, access_token_blacklist, Order
from security.token_security import BusinessJwtTokenAuth, BlacklistJwtTokenAuth
from .. import app, auth_fail


class BusinessData:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/{business_id}")
    def get_business_data(
            userUncast: BlacklistJwtTokenAuth,
            business_id: PathVariable("business_id"),
            response: HttpResponse,
            include_category_items: QueryParameter("include_category_items", bool),
    ):
        # TODO: Find where errors are caught and add a custom handler there.
        user: User = userUncast
        if business_id is None and isinstance(user, BusinessUser):
            business_id = user.business_id
        if business_id is None:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": "Must past a business id as query parameter - ?business_id=..."
            }

        business_id = ObjectId(business_id)
        business = Business.get_business_by_id(business_id)

        if business is None:
            response.status = HttpStatus.NOT_FOUND
            return f"Business with id {business_id} does not exist."

        result = business.__getstate__()
        result["categories"] = business.categories if not include_category_items else business.get_categories_with_items()

        return result

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/orders")
    def get_business_orders(
            userUncast: BusinessJwtTokenAuth,
            res: HttpResponse
    ):
        user: BusinessUser = userUncast

        business: Business = Business.get_business_by_id(user.business_id)
        if business is None:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Whoops looks like your business no longer exists"
            }

        return Order.get_orders(business.orders)

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business")
    def get_my_business_data(
            userUncast: BlacklistJwtTokenAuth,
            response: HttpResponse,
            include_category_items: QueryParameter("include_category_items", bool),
    ):
        return BusinessData.get_business_data(userUncast, None, response, include_category_items)

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.patch("/business")
    def update_business_data(
            user: BusinessJwtTokenAuth,
            business_update_data: RequestBody(BusinessUpdateData),
            response: HttpResponse,
    ):
        user: BusinessUser = user
        business_update_data: BusinessUpdateData

        updated = Business.update_business(
            user.business_id,
            business_update_data.location,
            business_update_data.name,
            business_update_data.contact.phone,
            business_update_data.contact.email,
            business_update_data.contact.instagram,
            business_update_data.contact.twitter,
            business_update_data.contact.facebook,
        )

        if updated is None:
            response.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Business doesn't exist"
            }

        return updated

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business")
    def request_business_creation(
            user: BlacklistJwtTokenAuth,
            request: HttpRequest,
            response: HttpResponse,
            business_data: RequestBody(parameter_type=BusinessCreate),

    ):
        user: Union[User, BusinessUser] = user
        if hasattr(user, "business_id"):
            response.status = HttpStatus.BAD_REQUEST
            return {'error': "You already own a business!"}

        if business_data.name is None or business_data.email is None or business_data.phone is None or business_data.longitude is None \
                or business_data.latitude is None or business_data.business_national_number is None or business_data.business_owner_id is None:
            response.status = HttpStatus.BAD_REQUEST
            return "Missing body parameters! Must include 'email', 'name', 'phone', 'longitude', 'latitude', 'business_national_number', 'owner_id'."

        if len(business_data.business_owner_id) < 10:
            response.status = HttpStatus.BAD_REQUEST
            return {'error': "Must pass the ID of the business owner."}

        business: Business = Business.create_business(
            business_data.name.strip(),
            Location(business_data.latitude, business_data.longitude),
            business_data.email.strip(),
            business_data.phone.strip(),
            base64.b64decode(business_data.business_owner_id),
            business_data.business_national_number
        )

        user = user.promote_to_business_user(user._id, business._id)
        newToken = user.build_access_token(sign=True)
        access_token_blacklist.add_to_blacklist(request.headers["authorization"][8:])
        return {
            "token": newToken,
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
