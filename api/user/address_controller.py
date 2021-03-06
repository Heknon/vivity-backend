from web_framework_v2 import RequestBody, HttpResponse, HttpStatus, QueryParameter

from api import app, auth_fail
from database import User, ShippingAddress
from security import BlacklistJwtTokenAuth


class AddressController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user/address")
    def get_addresses(
            jwt_res: BlacklistJwtTokenAuth,
    ):
        user: User = jwt_res
        return user.shipping_addresses

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/address")
    def add_address(
            jwt_res: BlacklistJwtTokenAuth,
            address: RequestBody(parameter_type=ShippingAddress),
            res: HttpResponse,
    ):
        user: User = jwt_res
        result = user.add_address(address)
        res.status = HttpStatus.CREATED
        return result.shipping_addresses

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/user/address")
    def delete_address(
            jwt_res: BlacklistJwtTokenAuth,
            index: QueryParameter("index", int),
            res: HttpResponse,
    ):
        user: User = jwt_res
        if index is None:
            res.status = HttpStatus.BAD_REQUEST
            return {
                'error': "Must pass query parameter 'index' of type 'int'"
            }
        if index < 0 or index >= len(user.shipping_addresses):
            res.status = HttpStatus.BAD_REQUEST

            if len(user.shipping_addresses) == 0:
                return {
                    'error': "There are no addresses to delete"
                }
            return {
                'error': f'Must be an index between 0 and {len(user.shipping_addresses) - 1}'
            }

        return user.remove_address(index).shipping_addresses
