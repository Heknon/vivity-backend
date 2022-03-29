from api import auth_fail, app
from security import BlacklistJwtTokenAuth


class OrderController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user/order")
    def get_orders():
        pass