__all__ = ["DocumentObject", "users_collection", "businesses_collection", "orders_collection", "User", "UserOptions", "LikedItems",
           "ShippingAddress", "Order", "OrderItem", "OrderHistory", "ModificationButtonDataType", "SelectedModificationButton"]

from pymongo import MongoClient, collection, database, TEXT

from .doc_object import DocumentObject

client: database.Database = MongoClient("localhost", 27017)["vivity"]

test_collection: collection.Collection = client.test
users_collection: collection.Collection = client.users
businesses_collection: collection.Collection = client.businesses
orders_collection: collection.Collection = client.orders

users_collection.create_index([("email", TEXT)], unique=True)

from .user import *
from .item import *

