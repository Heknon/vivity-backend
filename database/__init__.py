__all__ = ["DocumentObject", "users_collection", "businesses_collection", "orders_collection", "User", "UserOptions", "LikedItems",
           "ShippingAddress", "Order", "OrderItem", "OrderHistory", "ModificationButtonDataType", "SelectedModificationButton", "Image",
           "Color", "ModificationButton", "ModificationButtonSide", "Review", "Item", "ItemStoreFormat", "Location", "Category", "Contact",
           "BusinessUser"]

from bson import ObjectId
from pymongo import MongoClient, collection, database, TEXT

from .color import Color
from .doc_object import DocumentObject
from .image import Image
from .location import Location

client: database.Database = MongoClient("localhost", 27017)["vivity"]


test_collection: collection.Collection = client.test
users_collection: collection.Collection = client.users
businesses_collection: collection.Collection = client.businesses
orders_collection: collection.Collection = client.orders

users_collection.create_index([("email", TEXT)], unique=True)

# item_id = ObjectId()
# encoded = item_id.binary.decode("cp437")
#
# doc1 = test_collection.insert_one({
#     "it": {
#         item_id.binary.decode("cp437"): {
#             "cool": "!"
#         },
#         item_id.binary.decode("cp437") + "s": {
#             "cool": "!"
#         }
#     },
#     "some_other_field": {
#         "cool": 1
#     }
# })
#
# print(test_collection.count_documents({"_id": doc1.inserted_id}, limit=1))
#
# print(test_collection.find_one(
#     {"_id": doc1.inserted_id},
#     {f"it.{item_id.binary.decode('cp437')}": 1, "_id": 0}
# )["it"])

from .user import *
from database.business import *
