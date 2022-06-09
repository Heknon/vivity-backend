from bson import ObjectId
from web_framework_v2 import RequestBody, HttpResponse, HttpStatus

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
        return user.cart

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
            body: RequestBody(parameter_type=list),
            res: HttpResponse
    ):
        user: User = jwt_res

        cart_items = list(map(lambda json: CartItem(
            item_id=ObjectId(json.get("item_id", None)),
            quantity=json.get("quantity", None),
            modifiers_chosen=list(map(
                lambda mod_button: SelectedModificationButton(
                    name=mod_button.get("name", None),
                    selected_data=mod_button.get("selected_data", None),
                    data_type=ModificationButtonDataType._value2member_map_[mod_button.get("data_type", 0)],
                ),
                json.get("modifiers_chosen", None))
            ),
        ), body))

        result = user.cart.replace_items(cart_items).order
        res.status = HttpStatus.CREATED
        return result
