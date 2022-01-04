from typing import List


class OrderItem:
    def __init__(
            self,
            image_id,
            business_id: bytes,
            item_id: int,
            title: str,
            subtitle: str,
            description: str,
            price: float
    ):
        self.image_id = image_id
        self.business_id = business_id
        self.item_id = item_id
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.price = price


class Order:
    def __init__(
            self,
            purchase_date: str,
            items: List[OrderItem]
    ):
        self.purchase_date = purchase_date
        self.items = items


class PaymentData:
    def __init__(
            self,
            credit_card_number: str,
            year: int,
            month: int,
            cvv: int,
            cart: List[Order]
    ):
        self.credit_card_number = credit_card_number
        self.year = year
        self.month = month
        self.cvv = cvv
        self.cart = cart
