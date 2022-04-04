from typing import Union

from bson import ObjectId
from web_framework_v2 import QueryParameter, RequestBody, PathVariable, HttpRequest, HttpResponse, HttpStatus

from body import BusinessUpdateData, AuthorizedRouteRequestBody, DictNoNone
from database import Business, Location, User, BusinessUser, blacklist, Contact, Order
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
        business: Business = Business.get_business_by_id(user.business_id)

        if business is None:
            response.status = HttpStatus.UNAUTHORIZED
            return f"No business with ID {user.business_id}"

        contact = Contact.get_db_repr(business.contact)

        if hasattr(business_update_data, "contact") and type(business_update_data.contact) is dict:
            for field_name in contact.keys():
                lengthened = business.contact.lengthen_field_name(field_name)
                if lengthened not in business_update_data.contact:
                    continue

                new_value = business_update_data.contact[lengthened]
                contact[field_name] = new_value

        locs = set(business.location)
        if hasattr(business_update_data, "add_locations"):
            locations = [business_update_data.add_locations] if type(business_update_data.add_locations) is not list \
                else business_update_data.add_locations

            for location in locations:
                if type(location) is not dict:
                    continue

                longitude = location.get("longitude", None)
                latitude = location.get("latitude", None)
                if longitude is None or latitude is None:
                    continue

                locs.add(Location(longitude, latitude))

        if hasattr(business_update_data, "remove_locations"):
            locations = [business_update_data.remove_locations] if type(business_update_data.remove_locations) is not list \
                else business_update_data.remove_locations
            for location in locations:
                if type(location) is not dict:
                    continue

                longitude = location.get("longitude", None)
                latitude = location.get("latitude", None)
                if longitude is None or latitude is None:
                    continue

                newLoc = Location(longitude, latitude)
                if newLoc in locs:
                    locs.remove(newLoc)

        locations = list(locs)
        result = DictNoNone(
            name=business_update_data.name if hasattr(business_update_data, "name") else None,
            contact=contact,
            locations=list(map(Location.get_db_repr, locations))
        )

        business = business.update_fields(**result)
        return {
            "name": business.name,
            "contact": Contact.get_db_repr(business.contact, True),
            "locations": list(map(lambda loc: Location.get_db_repr(loc), business.location))
        }

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business")
    def request_business_creation(
            user: BlacklistJwtTokenAuth,
            request: HttpRequest,
            response: HttpResponse,
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
            response.status = HttpStatus.BAD_REQUEST
            return "Missing query parameters! Must include 'email', 'name', 'phone', 'longitude', 'latitude', 'business_national_number'."

        if len(business_owner_id) < 10:
            response.status = HttpStatus.BAD_REQUEST
            return {'error': "Must pass the ID of the business owner."}

        user: Union[User, BusinessUser] = user
        if hasattr(user, "business_id"):
            response.status = HttpStatus.BAD_REQUEST
            return {'error': "You already own a business!"}

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
        blacklist.add_to_blacklist(request.headers["authorization"][8:])
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
