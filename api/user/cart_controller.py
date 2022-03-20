import binascii

from bson import ObjectId
from web_framework_v2 import JwtTokenAuth, RequestBody, HttpResponse, HttpStatus

from api import app, auth_fail
from database import User, CartItem, SelectedModificationButton, ModificationButtonDataType
from security import BlacklistJwtTokenAuth


class CartController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user/cart")
    def get_cart_items_detailed(
            jwt_res: BlacklistJwtTokenAuth,
    ):
        user: User = jwt_res
        return user.cart.get_full_items()

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.put("/user/cart")
    def add_cart_items(
            jwt_res: BlacklistJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res
        result = user.cart.add_items(
            *list(map(lambda json: CartItem(
                item_id=json.get("item_id", None),
                amount=json.get("amount", None),
                modifiers_chosen=list(map(
                    lambda mod_button: SelectedModificationButton(
                        name=mod_button.get("name", None),
                        selected_data=mod_button.get("selected_data", None),
                        data_type=ModificationButtonDataType[mod_button.get("data_type", "").capitalize()],
                    ),
                    json.get("modifiers_chosen", None))
                ),
            ), body))
        )
        res.status = HttpStatus.CREATED
        return result

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.patch("/user/cart")
    def update_quantities(
            jwt_res: BlacklistJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res

        quantities = {key: value for key, value in body.items() if isinstance(key, int) and isinstance(value, int)}
        return user.cart.mass_update_quantity(quantities)

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/user/cart")
    def delete_items(
            jwt_res: BlacklistJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res

        user.cart.mass_remove(body)
        res.status = HttpStatus.NO_CONTENT

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/cart")
    def replace_cart_items(
            jwt_res: BlacklistJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res

        cart_items = list(map(lambda json: CartItem(
            item_id=ObjectId(json.get("item_id", None)),
            amount=json.get("amount", None),
            modifiers_chosen=list(map(
                lambda mod_button: SelectedModificationButton(
                    name=mod_button.get("name", None),
                    selected_data=mod_button.get("selected_data", None),
                    data_type=ModificationButtonDataType._value2member_map_[mod_button.get("data_type", 0)],
                ),
                json.get("modifiers_chosen", None))
            ),
        ), body))

        result = user.cart.replace_items(cart_items)
        res.status = HttpStatus.CREATED
        return result
