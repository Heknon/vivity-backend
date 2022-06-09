from typing import List

from database.business.item.selected_modification_button import SelectedModificationButton
from database.user.shipping_address import ShippingAddress


class OrderItem:
    def __init__(
            self,
            item_id: bytes,
            business_id: bytes,
            amount: int,
            price: float,
            selected_modifiers: List[SelectedModificationButton]
    ):
        self.business_id = business_id
        self.item_id = item_id
        self.amount = amount
        self.price = price
        self.selected_modifiers = selected_modifiers


class Order:
    def __init__(
            self,
            subtotal: float,
            shipping_cost: float,
            cupon_discount: float,
            total: float,
            cupon: str,
            address: ShippingAddress,
            items: List[OrderItem]
    ):
        self.subtotal = subtotal
        self.shipping_cost = shipping_cost
        self.cupon_discount = cupon_discount
        self.total = total
        self.cupon = cupon
        self.address = address
        self.items = items


class PaymentData:
    def __init__(
            self,
            credit_card_number: str,
            year: int,
            month: int,
            cvv: str,
            name: str,
            order: Order
    ):
        self.credit_card_number = credit_card_number
        self.year = year
        self.month = month
        self.cvv = cvv
        self.name = name
        self.order = order
