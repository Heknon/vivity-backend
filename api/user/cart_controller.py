from web_framework_v2 import JwtTokenAuth, RequestBody, HttpResponse, HttpStatus

from api import app
from database import User, CartItem, SelectedModificationButton, ModificationButtonDataType


class CartController:
    @staticmethod
    @JwtTokenAuth
    @app.get("/user/cart")
    def get_cart_items_detailed(
            jwt_res: JwtTokenAuth,
    ):
        user: User = jwt_res
        return user.cart.get_full_items()

    @staticmethod
    @JwtTokenAuth
    @app.put("/user/cart")
    def add_cart_items(
            jwt_res: JwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res
        result = user.cart.add_items(
            *list(map(lambda json: CartItem(
                item_id=json.get("item_id", None),
                amount=json.get("amount", None),
                selected_modification_button_data=list(map(
                    lambda mod_button: SelectedModificationButton(
                        name=mod_button.get("name", None),
                        selected_data=mod_button.get("selected_data", None),
                        data_type=ModificationButtonDataType[mod_button.get("data_type", "").capitalize()],
                    ),
                    json.get("selected_modification_button_data", None))
                ),
            ), body))
        )
        res.status = HttpStatus.CREATED
        return result

    @staticmethod
    @JwtTokenAuth
    @app.patch("/user/cart")
    def update_quantities(
            jwt_res: JwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res

        quantities = {key: value for key, value in body.items() if isinstance(key, int) and isinstance(value, int)}
        return user.cart.mass_update_quantity(quantities)

    @staticmethod
    @JwtTokenAuth
    @app.delete("/user/cart")
    def delete_items(
            jwt_res: JwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res

        user.cart.mass_remove(body)
        res.status = HttpStatus.NO_CONTENT

    @staticmethod
    @JwtTokenAuth
    @app.post("/user/cart")
    def replace_cart_items(
            jwt_res: JwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: User = jwt_res
        result = user.cart.replace_items(
            *list(map(lambda json: CartItem(
                item_id=json.get("item_id", None),
                amount=json.get("amount", None),
                selected_modification_button_data=list(map(
                    lambda mod_button: SelectedModificationButton(
                        name=mod_button.get("name", None),
                        selected_data=mod_button.get("selected_data", None),
                        data_type=ModificationButtonDataType[mod_button.get("data_type", "").capitalize()],
                    ),
                    json.get("selected_modification_button_data", None))
                ),
            ), body))
        )
        res.status = HttpStatus.CREATED
        return result
