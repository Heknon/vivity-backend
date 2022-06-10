import datetime
from typing import Dict

from bson import ObjectId
from pymongo import ReturnDocument
from web_framework_v2 import QueryParameter, RequestBody, HttpResponse, HttpStatus

from api import auth_fail, app
from body import PaymentData
from database import User, Order, orders_collection, BusinessUser, Business, Item, OrderItem, SelectedModificationButton, ShippingAddress, \
    cupon_collection
from database.user import OrderStatus
from security import BlacklistJwtTokenAuth, BusinessJwtTokenAuth


class OrderController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user/order")
    def get_orders(
            user_raw: BlacklistJwtTokenAuth,
            order_ids: QueryParameter("order_ids", list)
    ):
        user: User = user_raw
        if order_ids is None:
            return {
                "error": "Must pass query parameter 'order_ids'"
            }

        user_orders = set(user.order_history.orders)
        order_ids = map(lambda x: ObjectId(x), order_ids)
        order_ids = list(filter(lambda x: x in user_orders, order_ids))
        order_docs = orders_collection.find({"_id": {"$in": order_ids}})
        return list(map(lambda doc: Order.document_repr_to_object(doc), order_docs))

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order")
    def user_payment(
            token_data: BlacklistJwtTokenAuth,
            res: HttpResponse,
            payment_data: RequestBody(PaymentData)
    ):
        payment_data: PaymentData = payment_data
        user: User = token_data

        items = list(map(lambda x: ObjectId(x['item_id']), payment_data.order['items']))
        db_items = {value.id: value for value in Item.get_items(*items)}
        db_subtotal = 0
        frontend_subtotal = 0

        db_cupon_discount = 0
        frontend_cupon_discount = payment_data.order['cupon_discount']

        db_shipping = 0
        frontend_shipping = payment_data.order['shipping_cost']
        business_ids = set()

        for i in range(len(payment_data.order['items'])):
            frontend_item = payment_data.order['items'][i]
            db_item = db_items[ObjectId(frontend_item['item_id'])]

            if db_item.price != frontend_item['price']:
                res.status = HttpStatus.UNAUTHORIZED
                return {
                    "error": "Cannot process payment",
                    "reason": "Item costs changed while going through checkout"
                }

            db_subtotal += db_item.price * frontend_item['amount']
            frontend_subtotal += frontend_item['price'] * frontend_item['amount']

            business_ids.add(ObjectId(frontend_item['business_id']))

        # calculate cupon discount
        db_cupon_discount = db_subtotal * (OrderController.get_cupon_discount(user, payment_data.order['cupon'], res)['discount'])
        frontend_cupon_discount *= frontend_subtotal

        # calculate shipping
        db_shipping: float = OrderController.get_shipping_cost(user, {"items": payment_data.order['items'], "sa": payment_data.order['address']}, res)[
            'cost']

        frontend_total = payment_data.order['total']
        db_total = round(db_subtotal + db_shipping - db_cupon_discount, 3)
        if round(db_subtotal, 3) != round(frontend_subtotal, 3):
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Item costs changed while going through checkout"
            }

        elif round(db_cupon_discount, 3) != round(frontend_cupon_discount, 3):
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Cupon discount changed while going through checkout"
            }

        elif round(db_shipping, 3) != round(frontend_shipping, 3):
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Shipping cost changed while going through checkout"
            }

        elif db_total != round(frontend_total, 3):
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Total cost changed while going through checkout"
            }

        order_items = OrderController.build_order_items_from_unparsed_list(payment_data.order['items'])

        order = Order(
            _id=ObjectId(),
            order_date=datetime.datetime.now(),
            subtotal=db_subtotal,
            shipping_cost=db_shipping,
            cupon_discount=db_cupon_discount,
            total=db_total,
            shipping_address=ShippingAddress.document_repr_to_object(
                {ShippingAddress.LONG_TO_SHORT[field_name]: value for field_name, value in payment_data.order['address'].items()}, address_index=0),
            items=order_items
        )

        order = Order.save(order)
        for business_id in business_ids:
            Business.add_order_by_id(ObjectId(business_id), order.id)

        user.order_history.add_order(order.id)
        user.cart.replace_items([])

        res.status = HttpStatus.CREATED
        return order

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order/shipping")
    def get_shipping_cost(
            user_raw: BlacklistJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ) -> Dict[str, object]:
        if not isinstance(body, dict):
            return {
                "error": "Must pass a dict as body"
            }

        mapped_items = OrderController.build_order_items_from_unparsed_list(body['items'])
        address = {ShippingAddress.LONG_TO_SHORT[key]: value for key, value in body['address'].items()} if body.get('address',
                                                                                                                    None) is not None else None
        cost = 0

        for item in mapped_items:
            cost += item.price * item.amount * 0.01

        return {
            'cost': float(cost)
        }

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/order/cupon")
    def get_cupon_discount(
            user_raw: BlacklistJwtTokenAuth,
            cupon: QueryParameter("cupon"),
            res: HttpResponse
    ):
        return {
            'discount': float(cupon_collection.find()[0]['cupons'].get(cupon, 0))
        }

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order/status")
    def update_order_status(
            user_raw: BusinessJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        # TODO: change status only for owning business items
        user: BusinessUser = user_raw
        order_id = body.get('order_id', None)
        item_index = body.get('item_index', None)
        status = body.get('status', None)
        if status is None or order_id is None or item_index is None:
            res.status = HttpStatus.BAD_REQUEST
            return {
                'error': 'Must pass body fields "order_id", "status" and "item_index"'
            }

        status_max = len(OrderStatus._member_map_.values())
        if not isinstance(status, int) or status >= status_max:
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"'status' body field must be an integer between 0 and {status_max}"
            }

        if not isinstance(item_index, int) or item_index < 0:
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"'item_index' body field must be an integer"
            }

        order_id = ObjectId(order_id)
        business = Business.get_business_by_id(user.business_id)

        if business is None:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Whoops, looks like you don't own a business"
            }

        if order_id not in business.orders:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "This order doesn't exist!"
            }

        order = Order.get_order(order_id)
        if item_index >= len(order.items):
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": "There is no item with such an index."
            }

        if order.items[item_index].business_id != business.id:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "You cannot modify the status of this item."
            }

        order_doc = orders_collection.find_one_and_update({"_id": order_id}, {"$set": {f"it.{item_index}.sta": status}},
                                                          return_document=ReturnDocument.AFTER)
        return Order.document_repr_to_object(order_doc)

    @staticmethod
    def build_order_items_from_unparsed_list(items):
        order_items = []
        for item in items:
            item_dict = dict()

            for field_name, value in item.items():
                field_name = OrderItem.LONG_TO_SHORT[field_name]

                if field_name == 'sm':
                    item_dict[field_name] = [{SelectedModificationButton.LONG_TO_SHORT[name]: val for name, val in selected_modifier.items()} for
                                             selected_modifier in value]
                else:
                    item_dict[field_name] = value

            order_items.append(OrderItem.document_repr_to_object(item_dict))

        return order_items
