__all__ = ["DocumentObject", "users_collection", "businesses_collection", "orders_collection", "User", "UserOptions", "LikedItems",
           "ShippingAddress", "Order", "OrderItem", "OrderHistory", "ModificationButtonDataType", "SelectedModificationButton", "Image",
           "Color", "ModificationButton", "ModificationButtonSide", "Review", "Item", "ItemStoreFormat", "Location", "Category", "Contact",
           "BusinessUser", "blacklist_collection", "blacklist", "Business", "s3Bucket", "Cart", "CartItem"]

from pymongo import MongoClient, collection, database, TEXT, GEOSPHERE

from .S3Bucket import s3Bucket
from .color import Color
from .doc_object import DocumentObject
from .image import Image
from .location import Location

client: database.Database = MongoClient("localhost", 27017)["vivity"]

test_collection: collection.Collection = client.test
users_collection: collection.Collection = client.users
businesses_collection: collection.Collection = client.businesses
orders_collection: collection.Collection = client.orders
items_collection: collection.Collection = client.items
blacklist_collection: collection.Collection = client.blacklist

users_collection.create_index([("email", TEXT)], unique=True)
items_collection.create_index([("loc", GEOSPHERE)], name="item_location_index", unique=False)
businesses_collection.create_index([("loc", GEOSPHERE)], name="business_location_index", unique=False)

from .blacklist import Blacklist

blacklist = Blacklist()
from .user import *
from database.business import *
