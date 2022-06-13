__all__ = ["DocumentObject", "users_collection", "businesses_collection", "orders_collection", "User", "UserOptions", "LikedItems",
           "ShippingAddress", "Order", "OrderItem", "OrderHistory", "ModificationButtonDataType", "SelectedModificationButton", "Image",
           "Color", "ModificationButton", "ModificationButtonSide", "Review", "Item", "ItemStoreFormat", "Location", "Category", "Contact",
           "BusinessUser", "access_token_blacklist_collection", "access_token_blacklist", "Business", "s3Bucket", "Cart", "CartItem",
           "refresh_token_blacklist", "refresh_token_blacklist_collection", "TokenBlacklist", "items_collection", "unapproved_businesses_collection", "ShippingMethod"]

from pymongo import MongoClient, collection, database, TEXT, GEOSPHERE

from .S3Bucket import s3Bucket
from .color import Color
from .doc_object import DocumentObject
from .image import Image
from .location import Location

client: database.Database = MongoClient("localhost", 27017)["vivity"]

users_collection: collection.Collection = client.users
businesses_collection: collection.Collection = client.businesses
unapproved_businesses_collection: collection.Collection = client.unapproved_businesses
orders_collection: collection.Collection = client.orders
items_collection: collection.Collection = client.items
access_token_blacklist_collection: collection.Collection = client.access_blacklist
refresh_token_blacklist_collection: collection.Collection = client.refresh_blacklist
user_auth_collection: collection.Collection = client.user_auth
cupon_collection: collection.Collection = client.cupon

users_collection.create_index([("ml", 1)], name="email", unique=True)
items_collection.create_index([("loc", GEOSPHERE)], name="item_location_index", unique=False)
items_collection.create_index([
    ("tg", TEXT),
    ('bnm', TEXT),
    ("isf.ttl", TEXT),
    ("isf.stl", TEXT),
    ("isf.dsc", TEXT),
    ("cat", TEXT),
    ("br", TEXT),
],
    name="item_text_index",
    unique=False,
)
businesses_collection.create_index([("loc", GEOSPHERE)], name="business_location_index", unique=False)

from .blacklist import TokenBlacklist

access_token_blacklist = TokenBlacklist(
    access_token_blacklist_collection,
    60 * 60 * 5,
    "Access token blacklist"
)

refresh_token_blacklist = TokenBlacklist(
    refresh_token_blacklist_collection,
    60 * 60 * 24 * 7,
    "Refresh token blacklist"
)


from .user import *
from database.business import *
