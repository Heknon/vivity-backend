from enum import IntEnum


class OrderStatus(IntEnum):
    Processing = 0,
    Processed = 1,
    Shipping = 2,
    Shipped = 3,
    ReadyForPickup = 4,
    Complete = 5
